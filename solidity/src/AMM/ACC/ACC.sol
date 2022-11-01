// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;
//pragma solidity >= 0.8;

import "prb-math/PRBMathSD59x18.sol";
import "src/AMM/ACC/IBasePS.sol";
import "src/AMM/ACC/IACC.sol";


contract ACC is IACC {
    using PRBMathSD59x18 for int256;

    uint public beta;
    address[] public sources;
    int256 public n_err;
    int256 public n_obs;
    
    int256 public smallNum;
	
    constructor() {
	n_err = 0;
	n_obs = 0;
	beta = 0;
	//smallNum = 0.000001 * 10**18;
	smallNum = 0.0 * 10**18;
	
    }

    function addSource(address source) external {
	//TODO: check whether the source is IBasePS
	//TODO: remove redundent sources
	sources.push(source);
    }

    function getSources() external view returns (uint sourcesOut) {
	sourcesOut = sources.length;
    }

    function setBeta(uint new_beta) external {
	beta = new_beta;
    }

    function getBeta() external view returns (uint betaOut) {
	betaOut = beta;
    }
    
    
    function predict() external view returns(int256 lowerInterval, int256 upperInterval) {
	int256[] memory lowerIntervals = new int256[](sources.length);
	int256[] memory upperIntervals = new int256[](sources.length);
	int256[] memory edges = new int256[](2 * sources.length); //TODO: inefficient
	
	// handle a trivial case
	if( sources.length == 0 ) {
	    return (PRBMathSD59x18.MIN_SD59x18, PRBMathSD59x18.MAX_SD59x18);
	}

	// read prediction sets from all sources
	for( uint i=0; i<sources.length; i++ ) {
	    (int256 l, int256 u) = IBasePS(sources[i]).predict();
	    lowerIntervals[i] = l - smallNum;
	    upperIntervals[i] = u + smallNum;
	    edges[i] = l;
	    edges[sources.length + i] = u;
	}

	// compute votes for each interval edge
	uint[] memory vote = new uint[](edges.length);
	for( uint i=0; i<edges.length; i++ ) {
	    for( uint j=0; j<sources.length; j++ ) {
		if( lowerIntervals[j] <= edges[i] && edges[i] <= upperIntervals[j] ) {
		    vote[i] += 1;
		}
	    }
	}

	// find the majority edges, i.e., vote >= sources.length - beta, to construct a conservative interval
	lowerInterval = PRBMathSD59x18.MAX_SD59x18;
	upperInterval = PRBMathSD59x18.MIN_SD59x18;
	for( uint i=0; i<vote.length; i++ ) {
	    if( vote[i] < sources.length - beta ) {
		continue;
	    }
	    
	    if( lowerInterval > edges[i] ) {
		lowerInterval = edges[i];
	    }
	    
	    if( upperInterval < edges[i] ) {
		upperInterval = edges[i];
	    }
	}
	
	if( lowerInterval > upperInterval ) {
	    (lowerInterval, upperInterval) = (upperInterval, lowerInterval);
	}
    }

    
    /* function _scale() private pure returns (int256 s) { */
    /* 	s = PRBMathSD59x18.scale(); */
    /* } */

    
    /* function miscoverage(int256 obs) public view returns (int256 e) { */
    /* 	int256 score = _scoreFunc.getScore(obs); */
    /* 	require(score <= 1 * _scale(), "score is larger than one"); */

    /* 	if( score >= _threshold ) { */
    /* 	    e = 0; */
    /* 	} else { */
    /* 	    e = 1 * _scale(); */
    /* 	} */
    /* } */

    /* function getMeanMiscoverage() public view returns (int256 m) { */
    /* 	m = n_err.div(n_obs); */
    /* } */    
}