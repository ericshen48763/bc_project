from web3 import Web3
import json

class MerkleTree:
    def __init__(self, elements):
        self.elements = elements
        # 將原本的 sha256 替換為以太坊標準的 keccak256
        self.leaves = [self._hash_string(e) for e in elements]
        self.tree = self._build_tree(self.leaves)

    def _hash_string(self, data):
        """計算字串的 Keccak-256 雜湊"""
        return Web3.to_hex(Web3.keccak(text=data))

    def _hash_bytes(self, data_bytes):
        """計算二進制資料的 Keccak-256 雜湊"""
        return Web3.to_hex(Web3.keccak(data_bytes))

    def _build_tree(self, leaves):
        tree = [leaves]
        current_layer = leaves

        while len(current_layer) > 1:
            next_layer = []
            for i in range(0, len(current_layer), 2):
                left = current_layer[i]
                right = current_layer[i + 1] if i + 1 < len(current_layer) else current_layer[i]
                
                # OpenZeppelin 驗證邏輯：兩兩結合前必須先按數值排序
                if left > right:
                    left, right = right, left
                
                combined = bytes.fromhex(left[2:]) + bytes.fromhex(right[2:])
                next_layer.append(self._hash_bytes(combined))
            
            tree.append(next_layer)
            current_layer = next_layer
            
        return tree

    def get_root(self):
        return self.tree[-1][0] if self.tree else None

    def get_proof(self, element):
        if element not in self.elements:
            return None

        index = self.elements.index(element)
        proof = []
        
        for layer in self.tree[:-1]:
            is_right_node = index % 2 == 1
            if is_right_node:
                proof.append(layer[index - 1])
            else:
                if index + 1 < len(layer):
                    proof.append(layer[index + 1])
                else:
                    proof.append(layer[index])
            index //= 2
            
        return proof

# ================= 測試區 =================
if __name__ == "__main__":
    student_list = ["411185003", "411185039", "411185999", "411185888"]
    tree = MerkleTree(student_list)
    print("【全新 Keccak-256 Root】請拿這個去 Remix 重新部署合約：")
    print(tree.get_root())