// SPDX-License-Identifier: UNLICENSED
//pragma solidity ^0.8.13;
pragma solidity >=0.5;

import "forge-std/Test.sol";
import "../src/AMM/ACC/BasePS.sol";
import "prb-math/PRBMathSD59x18.sol";

contract BasePSTest is Test {
    KF1D public scoreFunc;
    MVP public ps;
    
    function setUp() public {
	scoreFunc = new KF1D(1 * 10**18, 1 * 10**18, 1 * 10**18, 0.00001 * 10**18);
	ps = new MVP(0.1 * 10**18, 100, 0.9 * 10**18);
    }

    using PRBMathSD59x18 for int256;
    function testMath() public {
	emit log_named_decimal_int("pi =", PRBMathSD59x18.pi(), 18);
	int256 sig = PRBMathSD59x18.sqrt(10**18 + 10**18);
	emit log_named_decimal_int("2 pi =", PRBMathSD59x18.pi().mul(2 * PRBMathSD59x18.scale()), 18);
	emit log_named_decimal_int("sqrt(2 pi) =", PRBMathSD59x18.pi().mul(2 * PRBMathSD59x18.scale()).sqrt(), 18);
	emit log_named_decimal_int("sig sqrt(2 pi) =", PRBMathSD59x18.pi().mul(2 * PRBMathSD59x18.scale()).sqrt().mul(sig), 18);

	emit log_named_decimal_int("floor(1.1) =", PRBMathSD59x18.floor(1.1 * 10**18), 18);
	emit log_named_uint("floor(1.1) =", uint(1.1 * 10**18) / 10**18);
	emit log_named_int("int256(1) =", int256(1));
	emit log_named_uint("threshold index 12 =", uint(12 * PRBMathSD59x18.scale()) / uint(PRBMathSD59x18.scale()));


    }

    function testGetScore() public {
	/* int256 score = scoreFunc.getScore(obs); */
	/* /\* int256 score, int256 sig, int256 Z, int256 L) = scoreFunc.getScore(obs); *\/ */
	
	
	/* emit log_named_decimal_int("score on 0 =", score, 18); */
	/* emit log_named_decimal_int("sig =", sig, 18); */

	/* emit log_named_decimal_int("Z =", Z, 18); */
	/* emit log_named_decimal_int("L =", L, 18); */

	emit log_named_decimal_int("score on 0.0 =", scoreFunc.getScore(int256(0)), 18);
	emit log_named_decimal_int("score on 0.5 =", scoreFunc.getScore(int256(0.5 * 10**18)), 18);
	emit log_named_decimal_int("score on 1.0 =", scoreFunc.getScore(int256(1 * 10**18)), 18);
	emit log_named_decimal_int("score on 1.5 =", scoreFunc.getScore(int256(1.5 * 10**18)), 18);
	emit log_named_decimal_int("score on 2.0 =", scoreFunc.getScore(int256(2 * 10**18)), 18);
	emit log_named_decimal_int("score on 4.0 =", scoreFunc.getScore(int256(4 * 10**18)), 18);

    
    }

    function testGetInterval() public {
	
	(int256 lowerInterval, int256 upperInterval) = scoreFunc.getInterval(0);
	
	emit log_named_decimal_int("lower interval at threshold 0 =", lowerInterval, 18);
	emit log_named_decimal_int("upper interval at threshold 0 =", upperInterval, 18);

	(lowerInterval, upperInterval) = scoreFunc.getInterval(0.1 * 10**18);
	
	emit log_named_decimal_int("lower interval at threshold 0.1 =", lowerInterval, 18);
	emit log_named_decimal_int("upper interval at threshold 0.1 =", upperInterval, 18);

    }
    
    function testUpdate() public {
	emit log_named_decimal_int("state mean before update =", scoreFunc.stateMean(), 18);
	emit log_named_decimal_int("state variance before update =", scoreFunc.stateVar(), 18);

	scoreFunc.update(0);
	
	emit log_named_decimal_int("state mean after update =", scoreFunc.stateMean(), 18);
	emit log_named_decimal_int("state variance after update =", scoreFunc.stateVar(), 18);
    }

    function testMVP() public {
	for( uint i=0; i<200; i++ ) {
	    emit log_string("====================");
	    int256 obs = int256(10 * 10**18) - int256(i * 10**18);
	    emit log_named_decimal_int("obs =", obs, 18);
	    emit log_named_decimal_int("threshold before update =", ps._threshold(), 18);
	    ps.update(obs);
	    emit log_string("after update====================");

	    (int256 l, int256 u) = ps.predict();
	    emit log_string("after pred====================");

	    emit log_named_decimal_int("threshold after update =", ps._threshold(), 18);
	    emit log_named_decimal_int("score =", ps._scoreFunc().getScore(obs), 18);

	    /* emit log_named_decimal_int("lowerInterval =", l, 18); */
	    /* emit log_named_decimal_int("upperInterval =", u, 18); */
	    /* emit log_named_decimal_int("interval length =", u - l, 18); */
	    /* emit log_named_decimal_int("state mean after update =", ps._scoreFunc().stateMean(), 18); */
	    /* emit log_named_decimal_int("state var after update =", ps._scoreFunc().stateVar(), 18); */
	    /* emit log_named_decimal_int("state noise sig =", ps._scoreFunc().stateNoiseLogSig().exp(), 18); */
	    /* emit log_named_decimal_int("obs noise sig =", ps._scoreFunc().obsNoiseLogSig().exp(), 18); */
	    /* emit log_named_decimal_int("max score =", ps._scoreFunc().maxScore(), 18); */
	    
	}
    }

    function testObserve() public {
	uint reserve0 = 1 * 10**18;
	uint reserve1 = 1 * 10**18;
	ps.update(reserve0, reserve1);
	assert(ps._obs() == 1 * 10**18);
    }
    
    function testKF1D() public {

	for( int i=0; i<200; i++ ) {
	    emit log_string("====================");
	    int256 obs = int256(i * 10**18);
	    emit log_named_decimal_int("obs =", obs, 18);

	    scoreFunc.update(obs);
	    emit log_named_decimal_int("state mean =", scoreFunc.stateMean(), 18);
	    emit log_named_decimal_int("state var =", scoreFunc.stateVar(), 18);
	    emit log_named_decimal_int("state noise sig =", scoreFunc.stateNoiseLogSig().exp(), 18);
	    emit log_named_decimal_int("obs noise sig =", scoreFunc.obsNoiseLogSig().exp(), 18);

	}
    }


    function testRand() public {
	emit log_named_decimal_uint("rand val =", ps._rand(), 18);
	emit log_named_decimal_uint("rand val =", ps._rand(), 18);
	emit log_named_decimal_uint("rand val =", ps._rand(), 18);

    }
}
