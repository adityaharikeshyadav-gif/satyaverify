// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract SatyaVerifyProvenance {
    enum EventType { REGISTERED, ANALYZED, VERIFIED, TRANSFERRED }

    struct ProvenanceRecord {
        bytes32 evidenceHash;
        bytes32 fileHash;
        uint256 timestamp;
        address actor;
        EventType eventType;
        string metadata;
    }

    mapping(bytes32 => ProvenanceRecord[]) public provenance;
    mapping(bytes32 => bool) public exists;
    event ProvenanceRecorded(bytes32 indexed evidenceId, EventType eventType, uint256 timestamp);

    function recordEvent(
        bytes32 evidenceId,
        bytes32 fileHash,
        EventType eventType,
        string calldata metadata
    ) external {
        require(!exists[evidenceId] || provenance[evidenceId].length > 0, "Invalid evidence");
        provenance[evidenceId].push(ProvenanceRecord({
            evidenceHash: evidenceId,
            fileHash: fileHash,
            timestamp: block.timestamp,
            actor: msg.sender,
            eventType: eventType,
            metadata: metadata
        }));
        exists[evidenceId] = true;
        emit ProvenanceRecorded(evidenceId, eventType, block.timestamp);
    }

    function getProvenance(bytes32 evidenceId) external view returns (ProvenanceRecord[] memory) {
        return provenance[evidenceId];
    }
}
