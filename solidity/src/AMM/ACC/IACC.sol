// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

interface IACC {
    //function getMeanMiscoverage() external view returns (int256 m);
    function addSource(address source) external;
    function getSources() external view returns (uint sourcesOut);

    function setBeta(uint new_beta) external;
    function predict() external view returns (int256 lowerInterval, int256 upperInterval); // no inputs as it uses all previous data

    function getBeta() external view returns (uint betaOut);
}

