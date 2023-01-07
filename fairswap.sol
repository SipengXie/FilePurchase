pragma solidity ^0.8.17;
// 考虑使该合约成为一个平台，其中每一个文件有对应的sender[fileRoot]，
// 对于每一个文件我们先考虑同时只有一个交换，对应接收者为receiver[fileRoot]，如果支持多个交换则是考虑receiver[fileRoot][i]
// 对应的keyCommit[fileRoot]，多个交换则是keyCommit[fileRoot][i]
// phase[fileRoot]，多个则是phase[fileRoot][i]
// 要求检查msg.sender == receive[fileRoot]([i])
// 如果同时只有一个交换，则应当在finshied stage后设置receiver[fileRoot] = NULL
// 为了防止receiver恶意complain about fileRoot，需要有一个haveFile[fileRoot]进行标记，并且receiver == receive[fileRoot] == msg.sender
contract fileSale {
    uint256 constant depth = 2; // depth of merkel tree = log2(n)
    uint256 constant length = 1; // length of each file chunk: length * 32bytes
    uint256 constant n = 4; // total number of file chunk
    uint256 constant cipherN = 7; // totoal number of cipher chunk
    bytes32 constant fileRoot = 0x5F509E99DB6F468DF1F245A28921C8BB3D53F8AA7CED8B2CAB75BDAC76F196A7; // Cid
    bytes32 constant keyCommit = 0x0322B47A386843FE8F1ACF782945C3BB624DF06ECD785A327F87406B9B95D8B9; // H(Key)
    bytes32 constant cipherRoot = 0x43E49F77EE2D216AEFB25FE2885B9A6C1A068EB546C2645C97AF2A27AD85255A; // H(C)
    bytes32 constant cipherPrimeCommit = 0x1DC94447293FC19DE74FACB65D26680233C1FDF5DB8FA594B6C0411372CCDC2C; //H(H(C+1))


    enum stage {
        created,
        initialized,
        accepted,
        keyRevealed,
        finished
    }
    stage public phase = stage.created;
    uint256 public timeout;

    address payable public sender; //XXXAddressSXXX;
    address payable public receiver;
    uint256 price; //XXXPriceAXXX; // in wei
    bytes32 public key;

    // function modifier to only allow calling the function in the right phase only from the correct party
    modifier allowed(address p, stage s) {
        require(phase == s);
        require(block.timestamp < timeout);
        require(msg.sender == p);
        _;
    }

    // go to next phase
    function nextStage() internal {
        phase = stage(uint256(phase) + 1);
        timeout = block.timestamp + 10 minutes;
    }

    function calc_cipher_n() internal pure returns(uint256) {
        uint256 count = n;
        uint256 ans = 0;
        while (count != 1) {
            if (count & 1 == 1) {
                count += 1;
            }
            ans += count;
            count = count >> 1;
        }
        return ans + 1;
    }

    // constructor is initialize function
    constructor(address payable _receiver, uint256 _price) {
        require(cipherN == calc_cipher_n());
        sender = payable(msg.sender);
        receiver = _receiver;
        price = _price;
        nextStage();
    }

    // function accept
    function accept(bytes32 acceptCommit) public payable allowed(receiver, stage.initialized) {
        require(msg.value >= price);
        require(cipherPrimeCommit == keccak256(abi.encodePacked(acceptCommit)));
        nextStage();
    }

    // function revealKey (key)
    function revealKey(bytes32 _key) public allowed(sender, stage.accepted) {
        require(keyCommit == keccak256(abi.encodePacked(_key)));
        key = _key;
        nextStage();
    }

    // function complain about wrong hash of file
    function noComplain() public allowed(receiver, stage.keyRevealed) {
        selfdestruct(sender);
    }

    // function complain about wrong hash of file
    function complainAboutRoot(bytes32 _Zm, bytes32[depth] calldata _proofZm)
        public
        allowed(receiver, stage.keyRevealed)
    {
        require(vrfy(cipherN - 1, _Zm, _proofZm)); // Zm appears in ciphertext
        if (cryptSmall(cipherN - 1, _Zm) != fileRoot) { // decrypt Zm != fileRoot
            selfdestruct(receiver);
        }
    }

    // function complain about wrong hash of two inputs
    // 相比起原来的fairswap合约，我们check the relationship between indexOut and indexIn
    function complainAboutLeaf(
        uint256 _indexOut,
        uint256 _indexIn,
        bytes32 _Zout,
        bytes32[length] calldata _Zin1,
        bytes32[length] calldata _Zin2,
        bytes32[depth]  calldata _proofZout,
        bytes32[depth]  calldata _proofZin
    ) public allowed(receiver, stage.keyRevealed) {
        require(vrfy(_indexOut, _Zout, _proofZout));
        bytes32 Xout = cryptSmall(_indexOut, _Zout);

        require(vrfy(_indexIn, keccak256(abi.encodePacked(_Zin1)), _proofZin));
        require(_proofZin[0] == keccak256(abi.encodePacked(_Zin2)));

        (uint256 st, uint256 nxt_st) = layer_start_calc(_indexIn);
        require(((_indexIn - st) >> 1) + nxt_st == _indexOut);

        if (
            Xout !=
            keccak256(
                abi.encodePacked(cryptLarge(_indexIn, _Zin1), cryptLarge(_indexIn + 1, _Zin2)))
            )
        {
            selfdestruct(receiver);
        }
    }

    // function complain about wrong hash of two inputs
    // 相比起原来的fairswap合约，我们check the relationship between indexOut and indexIn
    function complainAboutNode(
        uint256 _indexOut,
        uint256 _indexIn,
        bytes32 _Zout,
        bytes32 _Zin1,
        bytes32 _Zin2,
        bytes32[depth] calldata _proofZout,
        bytes32[depth] calldata _proofZin
    ) public allowed(receiver, stage.keyRevealed) {
        require(vrfy(_indexOut, _Zout, _proofZout));
        bytes32 Xout = cryptSmall(_indexOut, _Zout);

        require(vrfy(_indexIn, _Zin1, _proofZin));
        require(_proofZin[0] == _Zin2);

        (uint256 st, uint256 nxt_st) = layer_start_calc(_indexIn);
        require(((_indexIn - st) >> 1) + nxt_st == _indexOut);

        if (
            Xout !=
            keccak256(
                abi.encodePacked(cryptSmall(_indexIn, _Zin1), cryptSmall(_indexIn + 1, _Zin2))
            )
        ) {
            selfdestruct(receiver);
        }
    }

    // refund function is called in case some party did not contribute in time
    function refund() public {
        require(block.timestamp > timeout);
        if (phase == stage.accepted) selfdestruct(receiver);
        if (phase >= stage.keyRevealed) selfdestruct(sender);
    }

    // function to both encrypt and decrypt text chunks with key k
    // encrypt(decrypt) file chunk
    function cryptLarge(uint256 _index, bytes32[length] calldata _ciphertext)
        public
        view
        returns (bytes32[length] memory)
    {
        bytes32[length] memory temp;
        _index = _index * length;
        for (uint256 i = 0; i < length; i++) {
            temp[i] = keccak256(abi.encodePacked(_index, key)) ^ _ciphertext[i];
            _index++;
        }
        return temp;
    }

    // function to decrypt hashes of the merkle tree
    // encrypt(decrypt) merkel node
    function cryptSmall(uint256 _index, bytes32 _ciphertext)
        public
        view
        returns (bytes32)
    {
        return keccak256(abi.encodePacked(n + _index, key)) ^ _ciphertext;
    }

    // function to verify Merkle Tree proofs
    // This verification is working on the ciphertext merkel tree
    function vrfy(
        uint256 _index,
        bytes32 _value,
        bytes32[depth] calldata _proof
    ) public pure returns (bool) {
        for (uint8 i = 0; i < depth; i++) {
            if ((_index & (1 << i)) >> i == 1)
                _value = keccak256(abi.encodePacked(_proof[i], _value));
            else _value = keccak256(abi.encodePacked(_value, _proof[i]));
        }
        return (_value == cipherRoot);
    }

    function layer_start_calc(uint256 _index) internal pure returns (uint256, uint256) {
        if (_index < 0 || _index > cipherN) {
            return (0, 0);
        }
        uint256 st = 0;
        uint256 nxt_st = 0;
        uint256 cur_node_num = n;

        while (cur_node_num > 1) {
            if (cur_node_num % 2 == 1) {
                cur_node_num += 1;
            }
            nxt_st = st + cur_node_num;
            if (_index >= st && _index < nxt_st) {
                return (st, nxt_st);
            }

            st = nxt_st;
            cur_node_num >>= 1;
        }
        return (0 , 0);
    }

}
