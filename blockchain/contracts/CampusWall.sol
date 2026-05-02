// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/utils/cryptography/MerkleProof.sol";

contract CampusWall {
    bytes32 public merkleRoot;
    uint256 public nextPostId = 1; // 產生每一篇貼文的唯一 ID

    // 修改事件：加入 postId 和 parentId
    event ConfessionPosted(
        uint256 indexed postId, 
        uint256 indexed parentId, 
        string message
    );

    constructor(bytes32 _merkleRoot) {
        merkleRoot = _merkleRoot;
    }

    // 修改發文函數：要求傳入 parentId (0 代表新貼文，大於 0 代表回覆)
    function postMessage(
        string memory message, 
        uint256 parentId, 
        bytes32 leaf, 
        bytes32[] memory proof
    ) public {
        require(
            MerkleProof.verify(proof, merkleRoot, leaf),
            "Invalid Merkle Proof! You are not in the whitelist."
        );

        // 將貼文或留言寫入區塊鏈
        emit ConfessionPosted(nextPostId, parentId, message);
        nextPostId++;
    }

    function updateMerkleRoot(bytes32 _newRoot) public {
        merkleRoot = _newRoot;
    }
}