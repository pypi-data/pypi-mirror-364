#pragma once
#include <cstdint>
#include <cmath>
#include <algorithm>
#include <random>
#ifdef _OPENMP
#include <omp.h>
#endif

template<typename T>
void detectorIndices(uint32_t& ring_number1, uint32_t& ring_number2, uint32_t& ring_pos1, uint32_t& ring_pos2, const uint32_t blocks_per_ring, const uint32_t linear_multip,
	const bool no_modules, const bool no_submodules, const T moduleID1, const T moduleID2, const T submoduleID1, const T submoduleID2, const T rsectorID1,
	const T rsectorID2, const T crystalID1, const T crystalID2, const uint32_t cryst_per_block1, const uint32_t cryst_per_block2, const uint32_t cryst_per_block_z1, const uint32_t cryst_per_block_z2, const uint32_t transaxial_multip,
	const uint32_t rings) {

	// Detector numbers axially
	// Different versions for different cases
	if (no_modules && linear_multip > 1 && no_submodules) {
		ring_number1 = (rsectorID1 / blocks_per_ring) * cryst_per_block_z1 + crystalID1 / cryst_per_block1;
		ring_number2 = (rsectorID2 / blocks_per_ring) * cryst_per_block_z2 + crystalID2 / cryst_per_block2;
	}
	else if (rings == 0) {
		ring_number1 = 0;
		ring_number2 = 0;
	}
	else if (linear_multip == 1 && no_modules && no_submodules) {
		ring_number1 = rsectorID1;
		ring_number2 = rsectorID2;
	}
	else if (linear_multip == 1 && no_submodules) {
		ring_number1 = moduleID1;
		ring_number2 = moduleID2;
	}
	else if (linear_multip == 1 && !no_submodules) {
		ring_number1 = submoduleID1;
		ring_number2 = submoduleID2;
	}
	else if (!no_submodules) {
		if (transaxial_multip > 1) {
			ring_number1 = ((submoduleID1 / transaxial_multip) % linear_multip) * cryst_per_block_z1 + crystalID1 / cryst_per_block1;
			ring_number2 = ((submoduleID2 / transaxial_multip) % linear_multip) * cryst_per_block_z2 + crystalID2 / cryst_per_block2;
		}
		else {
			ring_number1 = (submoduleID1 % linear_multip) * cryst_per_block_z1 + crystalID1 / cryst_per_block1;
			ring_number2 = (submoduleID2 % linear_multip) * cryst_per_block_z2 + crystalID2 / cryst_per_block2;
		}
	}
	else {
		if (transaxial_multip > 1) {
			ring_number1 = ((moduleID1 / transaxial_multip) % linear_multip) * cryst_per_block_z1 + crystalID1 / cryst_per_block1;
			ring_number2 = ((moduleID2 / transaxial_multip) % linear_multip) * cryst_per_block_z2 + crystalID2 / cryst_per_block2;
		}
		else {
			ring_number1 = (moduleID1 % linear_multip) * cryst_per_block_z1 + crystalID1 / cryst_per_block1;
			ring_number2 = (moduleID2 % linear_multip) * cryst_per_block_z2 + crystalID2 / cryst_per_block2;
		}
	}
	// Detector number transaxially
	if (transaxial_multip > 1) {
		if (no_submodules) {
			ring_pos1 = (rsectorID1 % blocks_per_ring) * cryst_per_block1 * transaxial_multip + (crystalID1 % cryst_per_block1) + (moduleID1 % transaxial_multip) * cryst_per_block1;
			ring_pos2 = (rsectorID2 % blocks_per_ring) * cryst_per_block2 * transaxial_multip + (crystalID2 % cryst_per_block2) + (moduleID2 % transaxial_multip) * cryst_per_block2;
		}
		else {
			ring_pos1 = (rsectorID1 % blocks_per_ring) * cryst_per_block1 * transaxial_multip + (crystalID1 % cryst_per_block1) + (submoduleID1 % transaxial_multip) * cryst_per_block1;
			ring_pos2 = (rsectorID2 % blocks_per_ring) * cryst_per_block2 * transaxial_multip + (crystalID2 % cryst_per_block2) + (submoduleID2 % transaxial_multip) * cryst_per_block2;
		}
	}
	else {
		ring_pos1 = (rsectorID1 % blocks_per_ring) * cryst_per_block1 + (crystalID1 % cryst_per_block1);
		ring_pos2 = (rsectorID2 % blocks_per_ring) * cryst_per_block2 + (crystalID2 % cryst_per_block2);
	}
}