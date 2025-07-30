use alloy_dyn_abi::DynSolValue;
use alloy_primitives::U128;
use core_common::{
    Address,
    types::{
        identifiers::ChainVariant,
        primitives::{Bytes32, Hash, Keccak256, Signature, TimeValue},
        transaction::EpochId,
    },
    util::tokenize::Tokenizable,
};
use core_crypto::{eip191::HashEIP191, hash_without_prefix};
use core_macros::AbiToken;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

// TODO: The types in this file should be cleaned up given all of the
// refactors that took place in the Checkpoint and Registration facets.
// Additionally, these types would probably be better suited for an
// individual file rather than being lumped with all of the other
// transaction types.
#[derive(Debug, Clone, PartialEq, Default, Serialize, Deserialize, AbiToken)]
#[serde(rename_all = "camelCase")]
pub struct Checkpoint {
    /// Including the block number and hash to ensure that the checkpoint is
    /// only valid on the fork that the operator was tracking.
    /// Use u128 to align with the on-chain type.
    pub block_number: u128,
    pub block_hash: Hash,
    pub state_root: Hash,
    pub transaction_root: Hash,
}

impl From<SignedCheckpoint> for Checkpoint {
    fn from(signed_checkpoint: SignedCheckpoint) -> Self {
        Self {
            block_number: signed_checkpoint.block_number as u128,
            block_hash: signed_checkpoint.block_hash,
            state_root: signed_checkpoint.state_root,
            transaction_root: signed_checkpoint.transaction_root,
        }
    }
}

pub type SignedCheckpoints = HashMap<ChainVariant, SignedCheckpoint>;

/// Signed checkpoint data to be sent to the contract.
/// Corresponds to `OperatorDefs.CheckpointData` data on-chain
#[derive(Debug, Copy, Clone, PartialEq, Default, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
#[repr(C)]
pub struct SignedCheckpoint {
    /// Including the block number and hash to ensure that the checkpoint is
    /// only valid on the fork that the operator was tracking.
    // should use u128 to align with the on-chain type.
    // TODO: use u64 since u128 is not supported by Serde JSON, try to use u128
    // if revert to CBOR encoding.
    pub block_number: u64,
    pub block_hash: Hash,
    pub state_root: Hash,
    pub transaction_root: Hash,
    // TODO: Should this be included in checkpoints
    // submitted to the contracts for some reason? I don't really see the
    // value as of right now considering that it will (1) increase the cost
    // of check-pointing meaningfully and (2) isn't helpful in determining
    // how many trade mining periods have elapsed considering that trade
    // mining periods are measured in checkpoint epochs rather than time value
    // ticks.
    pub time_value: TimeValue,
    /// Including the signer to avoid needing to recover the signer from the
    /// signature if the signer is required to establish an order.
    pub signer: Address,
    /// Including the signature as a field for consistency with other
    /// structures
    pub signature: Signature,
}

#[cfg(not(target_family = "wasm"))]
core_common::impl_contiguous_marker_for!(SignedCheckpoint);

#[cfg(not(target_family = "wasm"))]
core_common::impl_unsafe_byte_slice_for!(SignedCheckpoint);

/// Signed checkpoint data to be sent to the contract.
/// Corresponds to `OperatorDefs.CheckpointData` data on-chain
///
/// This is a wrapper around the `SignedCheckpoint` type that includes the
/// contract address, chain ID, and epoch ID.
///
/// This is used to protect against replay attacks.
pub struct SignedCheckpointWithIntegrity {
    contract_address: Address,
    chain_id: u64,
    epoch_id: EpochId,
    checkpoint: SignedCheckpoint,
}

impl SignedCheckpointWithIntegrity {
    pub fn new(
        contract_address: Address,
        chain_id: u64,
        epoch_id: EpochId,
        checkpoint: SignedCheckpoint,
    ) -> Self {
        Self {
            contract_address,
            chain_id,
            epoch_id,
            checkpoint,
        }
    }
}

impl Keccak256<Hash> for SignedCheckpointWithIntegrity {
    fn keccak256(&self) -> Hash {
        let padded_epoch_id = Bytes32::from(self.epoch_id);
        let block_number = U128::from(self.checkpoint.block_number);
        let message = DynSolValue::Tuple(vec![
            self.contract_address.into_token(),
            self.chain_id.into_token(),
            padded_epoch_id.into_token(),
            block_number.into_token(),
            self.checkpoint.block_hash.into_token(),
            self.checkpoint.state_root.into_token(),
            self.checkpoint.transaction_root.into_token(),
        ])
        .abi_encode();
        hash_without_prefix(message).into()
    }
}

impl HashEIP191 for SignedCheckpointWithIntegrity {}

#[derive(Debug, Clone, PartialEq, Default, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CheckpointSubmission {
    pub checkpoint: Checkpoint,
    pub signatures: Vec<Signature>,
}

// TODO: It would be better to just encapsulate this in the AbiToken trait.
impl CheckpointSubmission {
    pub fn into_tokens_for_verification(self) -> DynSolValue {
        let payload = self.checkpoint.into_token();
        let signatures = DynSolValue::Array(
            self.signatures
                .iter()
                .map(|s| {
                    let vrs_signature = s.as_vrs();
                    DynSolValue::Bytes(vrs_signature.as_slice().to_vec())
                })
                .collect::<Vec<_>>(),
        );
        DynSolValue::Tuple(vec![payload, signatures])
    }
}
