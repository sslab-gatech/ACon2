// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;
//pragma solidity >= 0.8;

import "prb-math/PRBMathSD59x18.sol";

interface ISeqScoreFunc {
    //function initialize() public;
    function predict() external view returns (int256, int256); //TODO: do I need external
    function update(int256 obs) external;
    function getInterval(int256) external view returns (int256, int256);
    function getScore(int256) external view returns (int256);
}


interface IBasePS {
    /* function initialize() external; */
    function predict() external view returns (int256, int256); // no inputs as it uses all previous data
    function getThreshold() external view returns(int256);
    function getNoise() external view returns(int256 stateNoiseVar, int256 obsNoiseVar);
    function getMeanMiscoverage() external view returns (int256 m);

    //DBG
    function _rand() external view returns (uint256 p);

}

