// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

interface IACC {
    //function getMeanMiscoverage() external view returns (int256 m);
    function addSource(address source) external;
    function getSources() external view returns (uint sourcesOut);

    function setBeta(uint new_beta) external;
    function predict() external view returns (int256 lowerInterval, int256 upperInterval); // no inputs as it uses all previous data
    function eval() external view returns(int256 lowerInterval, int256 upperInterval, int256[] memory lowerIntervals, int256[] memory upperIntervals, int256[] memory observations);

    function getBeta() external view returns (uint betaOut);
}

