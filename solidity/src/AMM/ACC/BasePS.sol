// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;
//pragma solidity >= 0.8;

import "prb-math/PRBMathSD59x18.sol";
import "src/AMM/ACC/IBasePS.sol";

contract KF1D is ISeqScoreFunc {
    using PRBMathSD59x18 for int256;
    
    int256 public stateNoiseLogSig;
    int256 public stateNoiseLogSigMin;
    int256 public obsNoiseLogSig;
    int256 private learningRate;

    int256 public stateMean;
    int256 public stateVar;
    int256 public maxScore;

    
    constructor(int256 initStateNoiseLogSig, int256 initStateNoiseLogSigMin, int256 initObsNoiseLogSig, int256 initLearningRate) {
	stateNoiseLogSig = initStateNoiseLogSig;
	stateNoiseLogSigMin = initStateNoiseLogSigMin;
	obsNoiseLogSig = initObsNoiseLogSig;
	learningRate = initLearningRate;

	// the state is initialized to default values
	stateMean = 0;
	stateVar = 1 * _scale();
	maxScore = 1 * _scale();
    }

    
    function _scale() private pure returns (int256 s) {
	s = PRBMathSD59x18.scale();
    }

    
    function predict() public view returns (int256 predObsMean, int256 predObsVar) {
	predObsMean = stateMean;
	int256 obsNoiseSig = obsNoiseLogSig.exp();
	predObsVar = stateVar + obsNoiseSig.mul(obsNoiseSig);
    }

    
    function update(int256 obs) public {

	// update noise variances
	{
	    int256 w = stateNoiseLogSig.exp();
	    int256 v = obsNoiseLogSig.exp();
	    
	    int256 xi = (stateVar + w.mul(w) + v.mul(v)).sqrt();
	    int256 xi3 = xi.mul(xi).mul(xi);
	    int256 diffSq = (obs - stateMean).abs().mul((obs - stateMean).abs());
	    
	    // compute gradients of noise variances
	    int256 gradStateNoiseLogSig = (xi.inv() - diffSq.div(xi3)).mul(w).div(xi).mul(w);
	    int256 gradObsNoiseLogSig = (xi.inv() - diffSq.div(xi3)).mul(v).div(xi).mul(v);

	    // update
	    stateNoiseLogSig = stateNoiseLogSig - learningRate.mul(gradStateNoiseLogSig);
	    obsNoiseLogSig = obsNoiseLogSig - learningRate.mul(gradObsNoiseLogSig);

	    // truncate
	    if( stateNoiseLogSig < stateNoiseLogSigMin ) {
		stateNoiseLogSig = stateNoiseLogSigMin;
	    }
	}

	// update the current state
	{
	    // predict the current state before seeing the current observation
	    int256 stateNoiseSig = stateNoiseLogSig.exp();
	    int256 obsNoiseSig = obsNoiseLogSig.exp();
	    int256 stateNoiseVar = stateNoiseSig.mul(stateNoiseSig);
	    int256 obsNoiseVar = obsNoiseSig.mul(obsNoiseSig);

	    int256 predStateMean = stateMean;
	    int256 predStateVar = stateVar + stateNoiseVar;

	    // update the current state based on the current observation
	    int256 meanInno = obs - predStateMean;
	    int256 varInno = predStateVar + obsNoiseVar;
	    int256 optKalmanGain = predStateVar.mul(varInno.inv());

	    // update
	    stateMean = predStateMean + optKalmanGain.mul(meanInno);
	    stateVar = predStateVar - optKalmanGain.mul(predStateVar);
	}

	// update the max score
	{
	    (int256 predObsMean, int256 predObsVar) = predict();
	    maxScore = (predObsVar.mul(PRBMathSD59x18.pi()).mul(2 * _scale())).sqrt().inv().mul(2 * _scale());
	}

    }
	

    function getInterval(int256 t) public view returns (int256 lowerInterval, int256 upperInterval) {
	if (t == 0) {
	    // the largest interval
	    lowerInterval = PRBMathSD59x18.MIN_SD59x18;
	    upperInterval = PRBMathSD59x18.MAX_SD59x18;
	} else {
	    t = t.mul(maxScore);
	    (int256 predObsMean, int256 predObsVar) = predict();
	    int256 predObsSig = predObsVar.sqrt();

	    require(predObsSig > 0, "sig <= 0");
	    
	    int256 c = - (2 * _scale()).mul( t.ln() ) - (2 * _scale()).mul( predObsSig.ln() ) - (2 * _scale()).mul(PRBMathSD59x18.pi()).ln();
	    if( c < 0 ){
		// return the largest interval
		/* lowerInterval = predObsMean; */
		/* upperInterval = predObsMean; */
		
		// return an invalid interval
		lowerInterval = PRBMathSD59x18.MAX_SD59x18;
		upperInterval = PRBMathSD59x18.MIN_SD59x18;
	    } else {
		lowerInterval = predObsMean - predObsSig.mul(c.sqrt());
		upperInterval = predObsMean + predObsSig.mul(c.sqrt());
	    }
	}
    }

    function getScore(int256 obs) public view returns (int256 score) {
	(int256 predObsMean, int256 predObsVar) = predict();
	int256 sig = predObsVar.sqrt();
	int256 Z = PRBMathSD59x18.pi().mul(2 * _scale()).sqrt().mul(sig);
	int256 ndiff = (obs - predObsMean).div(sig).abs();
	int256 L = (- ndiff.mul(ndiff).div(2 * _scale())).exp();
	score = L.div(Z);
	score = score.div(maxScore);
	require(score >= 0, "score < 0");
    }

}


contract MVP is IBasePS {
    using PRBMathSD59x18 for int256;
    
    KF1D public _scoreFunc;
    int256 private _alpha;
    int256 public _threshold; //TODO: private
    uint private _numOfBins;
    int256 private _eta;
    int256[] private _corrWeight;
    int256[] private _thresCount;
    int256 private _r = 1000 * PRBMathSD59x18.scale();

    int256 public _obs;
    int256 public _n_err;
    int256 public _n_obs;
    int256 public _lowerInterval;
    int256 public _upperInterval;

    constructor(int256 alpha, uint numOfBins, int256 initEta) {
	//_scoreFunc = new KF1D(1 * 10**18, 1 * 10**18, 0.01 * 10**18);
	/* _scoreFunc = new KF1D(0, 0, 0.001 * 10**18); */
	//_scoreFunc = new KF1D(1 * 10**18, 1 * 10**18, 0.00001 * 10**18);
	_scoreFunc = new KF1D(0 * 10**18, -1 * 10**18, 0 * 10**18, 0.001 * 10**18);
	
	_alpha = alpha;
	_threshold = 0;
	_numOfBins = numOfBins;
	_eta = initEta;
	_corrWeight = new int256[](_numOfBins);
	_thresCount = new int256[](_numOfBins);
	_obs = 0;
	_lowerInterval = 0;
	_upperInterval = 0;
	_n_err = 0;
	_n_obs = 0;
    }


    function setAlpha(int256 new_alpha) external {
	_alpha = new_alpha;
    }

    function getAlpha() external view returns (int256 alphaOut) {
	alphaOut = _alpha;
    }

    function getEvalData() external view returns (int256 lowerInterval, int256 upperInterval, int256 obsOut) {
	lowerInterval = _lowerInterval;
	upperInterval = _upperInterval;
	obsOut = _obs;
    }


    function predict() public view returns(int256 lowerInterval, int256 upperInterval) {
	(lowerInterval, upperInterval) = _scoreFunc.getInterval(_threshold);
    }

    function getThreshold() external view returns(int256 threshold) {
	threshold = _threshold;
    }

    function getObsPrediction() external view returns(int256 predObsMean, int256 predObsVar) {
	return _scoreFunc.predict();
    }

    function getNoise() external view returns(int256 stateNoiseVar, int256 obsNoiseVar) {
	stateNoiseVar = _scoreFunc.stateNoiseLogSig().exp().mul(_scoreFunc.stateNoiseLogSig().exp());
	obsNoiseVar = _scoreFunc.obsNoiseLogSig().exp().mul(_scoreFunc.obsNoiseLogSig().exp());
    }

    function _normalizeFunc(int256 n) private pure returns (int256 z) {
	require(n >= 0, "n < 0");

	int256 a = n + 1 * _scale();
	int256 b = (n + 2 * _scale()).log2();
	z = a.mul(b).mul(b).sqrt();
    }

    
    function _rand() public view returns (uint256 p) {
	// not safe
	p = uint(keccak256(abi.encodePacked(block.difficulty, block.timestamp))) % 10**18;
    }
    

    function _scale() private pure returns (int256 s) {
	s = PRBMathSD59x18.scale();
    }

    
    function _findThreshold() public view returns (int256 threshold) {

	int256 prevWeight =
	    _eta.mul(_corrWeight[0]).div(_normalizeFunc(_thresCount[0])).exp() -
	    (-_eta).mul(_corrWeight[0]).div(_normalizeFunc(_thresCount[0])).exp();
	
	bool pos;
	if( prevWeight > 0 ) {
	    pos = true;
	} else {
	    pos = false;
	}

	for(uint i=1; i<_numOfBins; i++) {

	    int256 currWeight =
		_eta.mul(_corrWeight[i]).div(_normalizeFunc(_thresCount[i])).exp() -
		(-_eta).mul(_corrWeight[i]).div(_normalizeFunc(_thresCount[i])).exp();

	    if( currWeight > 0 ) {
		pos = true;
	    } else {
		pos = false;
	    }

	    if( currWeight.mul(prevWeight) <= 0 ) {
		int256 Z = currWeight.abs() + prevWeight.abs();
		uint256 b;
		if( Z == 0 ) {
		    b = uint256(1 * _scale());
		} else {
		    b = uint256(currWeight.abs().div(Z));
		}

		if( _rand() <= b ) {
		    return 1*_scale() - ((int256(i) * _scale()).div(int256(_numOfBins) * _scale()) - _r.mul(int256(_numOfBins) * _scale()).inv());
		    /* return ((int256(i) * _scale()).div(int256(_numOfBins) * _scale()) - _r.mul(int256(_numOfBins) * _scale()).inv()); */

		} else {
		    return 1*_scale() - (int256(i) * _scale()).div(int256(_numOfBins) * _scale());
		    /* return (int256(i) * _scale()).div(int256(_numOfBins) * _scale()); */
		}
	    }
	    prevWeight = currWeight;
	}

	if( pos ) {
	    return 1 * _scale();
	} else {
	    return 0;
	}
    }

    
    function miscoverage(int256 obs) public view returns (int256 e) {
	int256 score = _scoreFunc.getScore(obs);
	//require(score <= 1 * _scale(), "score is larger than one");

	/* // score based miscoverage */
	/* if( score >= _threshold ) { */
	/*     e = 0; */
	/* } else { */
	/*     e = 1 * _scale(); */
	/* } */


	// interval-based miscoverage
	(int256 lowerInterval, int256 upperInterval) = predict();
	if( (lowerInterval <= obs) && (obs <= upperInterval) ) {
	    return 0;
	} else {
	    return 1 * _scale();
	}
    }

    function getMeanMiscoverage() public view returns (int256 m) {
	m = _n_err.div(_n_obs);
    }

    function update(uint reserve0, uint reserve1) public returns(int256 threshold) {
	int256 obs = int256(reserve0).div(int256(reserve1));
	// keep data for evaluation
	_obs = obs;
	(_lowerInterval, _upperInterval) = predict();
	
	// update a threshold
	threshold = update(obs);
    }


    function update(int256 obs) public returns(int256 threshold) {


	// update stats
	require(_threshold >= 0, "_threshold < 0");
	require(_threshold <= _scale(), "_threshold > 1");
	    
	uint binIdx = uint((1*_scale() - _threshold).mul(int256(_numOfBins) * _scale()) + _r.inv().div(2 * _scale())) / uint(_scale());
	/* uint binIdx = uint((_threshold).mul(int256(_numOfBins) * _scale()) + _r.inv().div(2 * _scale())) / uint(_scale()); */

	if(binIdx > _numOfBins - 1) {
	    binIdx = _numOfBins - 1;
	}
	require(binIdx >= 0, "binIdx < 0");
	require(binIdx < _numOfBins, "binIdx >= _numOfBins");

	int256 miscov = miscoverage(obs);
	_n_err += miscov;
	_n_obs += 1 * _scale();
	
	_thresCount[binIdx] += 1 * _scale();
	_corrWeight[binIdx] += (_alpha - miscov);

	// update the current threshold
	_threshold = _findThreshold();
	threshold = _threshold;

	// update the score function
	_scoreFunc.update(obs);


    }

    
}
