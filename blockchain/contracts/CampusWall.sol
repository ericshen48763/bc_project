// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// 直接匯入 OpenZeppelin 寫好的 MerkleProof 函式庫
import "@openzeppelin/contracts/utils/cryptography/MerkleProof.sol";

contract CampusWall {
    // 儲存從 Python 後端算出來的，代表「全校名單」的唯一 Root Hash
    bytes32 public merkleRoot;

    // 定義一個事件，當有人發文成功時，將訊息廣播出去
    event ConfessionPosted(string message);

    // 部署合約時，由管理員將 Root 存入
    constructor(bytes32 _merkleRoot) {
        merkleRoot = _merkleRoot;
    }

    /**
     * @dev 匿名發文函數
     * @param message 靠北牆的留言內容
     * @param leaf 該學生的專屬身分 Hash (由後端發放)
     * @param proof 證明路徑的陣列 (由後端發放)
     */
    function postMessage(string calldata message, bytes32 leaf, bytes32[] calldata proof) external {
        
        // 1. 密碼學驗證：檢查這個 proof 和 leaf 能不能拼湊出我們存好的 merkleRoot
        // MerkleProof.verify 會回傳 true 或 false
        bool isValid = MerkleProof.verify(proof, merkleRoot, leaf);
        
        // 如果驗證失敗，交易會直接被 revert 撤銷，並顯示錯誤訊息
        require(isValid, "Invalid Merkle Proof! You are not in the whitelist.");

        // 2. 驗證通過，將留言寫入區塊鏈歷史中 (透過 emit 事件)
        emit ConfessionPosted(message);
    }
    
    // 未來可以新增一個函數，允許管理員在每個新學期更新 merkleRoot
    function updateMerkleRoot(bytes32 _newRoot) external {
        // 這裡需要加上權限控制 (例如 onlyOwner)
        merkleRoot = _newRoot;
    }
}