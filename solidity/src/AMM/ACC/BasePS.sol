// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;
//pragma solidity >= 0.8;

import "prb-math/PRBMathSD59x18.sol";
import "src/AMM/ACC/IBasePS.sol";

contract KF1D is ISeqScoreFunc {
    using PRBMathSD59x18 for int256;
    
    int256 public stateNoiseLogSig;
    int256 public obsNoiseLogSig;
    int256 private learningRate;

    /* int256 private transModel = 1; */
    /* int256 private obsModel = 1; */
    int256 public stateMean;
    int256 public stateVar;

    
    constructor(int256 initStateNoiseLogSig, int256 initObsNoiseLogSig, int256 initLearningRate) {
	stateNoiseLogSig = initStateNoiseLogSig;
	obsNoiseLogSig = initObsNoiseLogSig;
	learningRate = initLearningRate;

	// the state is initialized to default values
	stateMean = 0;
	stateVar = 1 * 10**18;
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

	stateMean = predStateMean + optKalmanGain.mul(meanInno);
	stateVar = predStateVar - optKalmanGain.mul(predStateVar);
	}

	{
	    // update noise variances
	    int256 stateNoiseSig = stateNoiseLogSig.exp();
	    int256 obsNoiseSig = obsNoiseLogSig.exp();
	    int256 stateNoiseVar = stateNoiseSig.mul(stateNoiseSig);
	    int256 obsNoiseVar = obsNoiseSig.mul(obsNoiseSig);
	
	    int256 sigAll = (stateVar + stateNoiseVar + obsNoiseVar).sqrt();
	    int256 sigAll3 = sigAll.mul(sigAll).mul(sigAll);
	    int256 diffSq = (obs - stateMean).abs().mul((obs - stateMean).abs());
	    
	// compute gradients of noise variances
	/* int256 gradStateNoiseLogSig = (stateNoiseSig.mul(-2 * _scale())). */
	/*     mul( sigAll.inv() - diffSq.mul(sigAll3.inv()) ). */
	/*     mul( sigAll.inv() - (stateVar + stateNoiseVar).mul((2 * _scale()).inv()).mul(sigAll3.inv()) ). */
	/*     mul( stateNoiseSig ); */
	    int256 gradObsNoiseLogSig = (obsNoiseSig.mul(2 * _scale() )).
		mul( sigAll.inv() - diffSq.mul(sigAll3.inv()) ).
		mul( (stateVar + stateNoiseVar).mul((2 * _scale()).inv()).mul(sigAll3.inv()) ).
		mul( obsNoiseSig );
	
	// update state and observation noise variances
	/* int256 stateNoiseSig = (stateNoiseVar.sqrt() - learningRate.mul(gradStateNoiseSig)).abs(); */
	/* stateNoiseVar = stateNoiseSig.mul(stateNoiseSig); */
	    
	/* stateNoiseLogSig = stateNoiseLogSig - learningRate.mul(gradStateNoiseLogSig); */
	
	/* int256 obsNoiseSig = (obsNoiseVar.sqrt() - learningRate.mul(gradObsNoiseSig)).abs(); */
	/* obsNoiseVar = obsNoiseSig.mul(obsNoiseSig); */
	    
	    /* obsNoiseLogSig = obsNoiseLogSig - learningRate.mul(gradObsNoiseLogSig); */
	}
    }
	

    function getInterval(int256 t) public view returns (int256 lowerInterval, int256 upperInterval) {
	if (t == 0) {
	    // the largest interval
	    lowerInterval = PRBMathSD59x18.MIN_SD59x18;
	    upperInterval = PRBMathSD59x18.MAX_SD59x18;
	} else {
	    (int256 predObsMean, int256 predObsVar) = predict();
	    int256 predObsSig = predObsVar.sqrt();

	    require(predObsSig > 0, "sig <= 0");
	    require(t > 0, "t <= 0");
	    
	    int256 c = - (2 * PRBMathSD59x18.scale()).mul( t.ln() ) - (2 * PRBMathSD59x18.scale()).mul( predObsSig.ln() ) - (2 * PRBMathSD59x18.scale()).mul(PRBMathSD59x18.pi()).ln();
	    if( c < 0 ){
		// return a zero length interval
		lowerInterval = predObsMean;
		upperInterval = predObsMean;
	    } else {
		lowerInterval = predObsMean - predObsSig.mul(c);
		upperInterval = predObsMean + predObsSig.mul(c);
	    }
	}
    }

    function getScore(int256 obs) public view returns (int256 score) {
	//score = norm.pdf(obs.item(), loc=state_pred['mu'].item(), scale=(state_pred['cov'] + tc.exp(self.obs_noise)).sqrt().item())
	(int256 predObsMean, int256 predObsVar) = predict();
	int256 sig = predObsVar.sqrt();
	int256 Z = PRBMathSD59x18.pi().mul(2 * PRBMathSD59x18.scale()).sqrt().mul(sig);
	int256 ndiff = (obs - predObsMean).div(sig).abs();
	int256 L = (- ndiff.mul(ndiff).div(2 * PRBMathSD59x18.scale())).exp();
	score = L.div(Z);
	require(score >= 0, "score < 0");
    }

}


contract SpecialMVP is IBasePS {
    using PRBMathSD59x18 for int256;
    
    KF1D public _scoreFunc;
    int256 private _alpha;
    int256 public _threshold; //TODO: private
    uint private _numOfBins;
    int256 private _eta;
    int256[] private _corrWeight;
    int256[] private _thresCount;
    int256 private _r = 1000 * PRBMathSD59x18.scale();

    int256 public n_err;
    int256 public n_obs;
    

    constructor(int256 alpha, uint numOfBins, int256 initEta) {
	//_scoreFunc = new KF1D(1 * 10**18, 1 * 10**18, 0.01 * 10**18);
	_scoreFunc = new KF1D(0, 0, 0.001 * 10**18);
	_alpha = alpha;
	_threshold = 0;
	_numOfBins = numOfBins;
	_eta = initEta;
	_corrWeight = new int256[](_numOfBins);
	_thresCount = new int256[](_numOfBins);
	n_err = 0;
	n_obs = 0;
    }

    
    function predict() public view returns(int256 lowerInterval, int256 upperInterval) {
	(lowerInterval, upperInterval) = _scoreFunc.getInterval(_threshold);
    }

    function getThreshold() external view returns(int256 threshold) {
	threshold = _threshold;
    }

    function getNoise() external view returns(int256 stateNoiseVar, int256 obsNoiseVar) {
	stateNoiseVar = _scoreFunc.stateNoiseLogSig().exp().mul(_scoreFunc.stateNoiseLogSig().exp());
	obsNoiseVar = _scoreFunc.obsNoiseLogSig().exp().mul(_scoreFunc.obsNoiseLogSig().exp());
    }

    function _normalizeFunc(int256 n) private pure returns (int256 z) {
	require(n >= 0, "n < 0");

	int256 a = n + 1 * _scale();
	int256 b = (n + 2 * _scale()).log2();
	z = a.sqrt().mul(b);
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
	    } /* else { */
	    /* 	pos = false; */
	    /* } */

	    if( currWeight.mul(prevWeight) <= 0 ) {
		int256 Z = currWeight.abs() + prevWeight.abs();
		uint256 b;
		if( Z == 0 ) {
		    b = uint256(1 * _scale());
		} else {
		    b = uint256(currWeight.abs().div(Z));
		}

		if( _rand() <= b ) {
		    return (int256(i) * _scale()).div(int256(_numOfBins) * _scale()) - _r.mul(int256(_numOfBins) * _scale()).inv();
		    /* return threshold; */
		} else {
		    return (int256(i) * _scale()).div(int256(_numOfBins) * _scale());
		    /* return threshold; */
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
	require(score <= 1 * _scale(), "score is larger than one");

	if( score >= _threshold ) {
	    e = 0;
	} else {
	    e = 1 * _scale();
	}
    }

    function getMeanMiscoverage() public view returns (int256 m) {
	m = n_err.div(n_obs);
    }

    function update(uint reserve0, uint reserve1) public returns(int256 threshold) {
	int256 price = int256(reserve0).div(int256(reserve1));
	threshold = update(price);
    }

    function _updateState(uint reserve0, uint reserve1) public {
	int256 obs = int256(reserve0).div(int256(reserve1));

	// update stats
	uint binIdx = uint(_threshold.mul(int256(_numOfBins) * _scale()) + _r.inv().div(2 * _scale())) / uint(_scale());
	if(binIdx > _numOfBins - 1) {
	    binIdx = _numOfBins - 1;
	}

	int256 miscov = miscoverage(obs);
	n_err = n_err + miscov;
	n_obs = n_obs + 1 * _scale();
	
	_thresCount[binIdx] += 1 * _scale();
	_corrWeight[binIdx] += (_alpha - miscov);
    }

    function _updateThreshold(int256 threshold) public {
	_threshold = threshold;
    }

    function _updateScoreFunc(uint reserve0, uint reserve1) public {
	int256 obs = int256(reserve0).div(int256(reserve1));
	_scoreFunc.update(obs);
    }

    function update(int256 obs) public returns(int256 threshold) {
	
	// update stats
	uint binIdx = uint(_threshold.mul(int256(_numOfBins) * _scale()) + _r.inv().div(2 * _scale())) / uint(_scale());
	if(binIdx > _numOfBins - 1) {
	    binIdx = _numOfBins - 1;
	}

	int256 miscov = miscoverage(obs);
	n_err = n_err + miscov;
	n_obs = n_obs + 1 * _scale();
	
	_thresCount[binIdx] += 1 * _scale();
	_corrWeight[binIdx] += (_alpha - miscov);

	// update the current threshold
	_threshold = _findThreshold();
	threshold = _threshold;

	// update the score function
	_scoreFunc.update(obs);
    }

    
}
