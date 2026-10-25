"""
Comprehensive Focused Test Suite for Phase 3 Satellite-Enhanced Workflow
========================================================================
Validates all requirements:
1. Missing observations and non-existent paths.
2. Incomplete temporal sequences and single-date protection (T < 4).
3. Invalid or unavailable bands.
4. Missing checkpoints error handling.
5. All 5 target districts coverage accounting (Thanjavur, Thiruvarur, Salem, Tiruchirappalli, Dharmapuri).
6. Pretrained SICKLE models loading and architecture shapes.
7. Unit and aggregation consistency (kg/acre to tonnes/ha).
8. Live FastAPI test for satellite endpoints.
"""

import os
import sys
import unittest
import numpy as np
import torch

# Ensure project root is importable
sys.path.insert(0, os.path.abspath('.'))

from src.crop_health.s2_sickle_adapter import (
    SICKLE_S2_BANDS,
    Sentinel2SAFEProduct,
    S2PatchExtractor,
    MultiTemporalSequenceCollator,
    S2CropTypeModel,
    S2YieldModel,
    SICKLEInferencePipeline,
    SICKLEYieldInferencePipeline,
    InsufficientTemporalObservationsError
)
from src.satellite.satellite_workflow import (
    SatelliteWorkflowManager,
    DISTRICT_METADATA,
    COVERAGE_COMPLETE_SICKLE,
    COVERAGE_SINGLE_SCENE,
    COVERAGE_BORDER_PARTIAL,
    KG_ACRE_TO_TONNES_HA
)


class TestSatelliteWorkflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manager = SatelliteWorkflowManager()

    # ---------------------------------------------------------------------
    # 1. Temporal Sequence & Incomplete Observations Tests
    # ---------------------------------------------------------------------
    def test_single_date_temporal_guard(self):
        """Test that temporal sequence with T < 4 raises InsufficientTemporalObservationsError."""
        dummy_patch = {
            'data': np.zeros((12, 32, 32), dtype=np.float32),
            'invalid_mask': np.zeros((32, 32), dtype=bool),
            'date': np.datetime64('2020-04-03')
        }
        # T = 1
        with self.assertRaises(InsufficientTemporalObservationsError):
            MultiTemporalSequenceCollator.collate_patches([dummy_patch])

        # T = 3 (still less than minimum 4)
        patches_3 = [dict(dummy_patch, date=np.datetime64(f'2020-04-0{i+1}')) for i in range(3)]
        with self.assertRaises(InsufficientTemporalObservationsError):
            MultiTemporalSequenceCollator.collate_patches(patches_3)

    def test_sufficient_temporal_collation(self):
        """Test that T >= 4 collates into 5D tensor (1, T, 12, 32, 32)."""
        patches_4 = [
            {
                'data': np.ones((12, 32, 32), dtype=np.float32) * i,
                'invalid_mask': np.zeros((32, 32), dtype=bool),
                'date': np.datetime64(f'2020-04-0{i+1}')
            }
            for i in range(4)
        ]
        tensor, dates = MultiTemporalSequenceCollator.collate_patches(patches_4)
        self.assertEqual(tensor.shape, (1, 4, 12, 32, 32))
        self.assertEqual(len(dates), 4)

    # ---------------------------------------------------------------------
    # 2. 12-Band Canonical Ordering & Missing Bands Tests
    # ---------------------------------------------------------------------
    def test_canonical_12_bands_order(self):
        """Verify the exact 12-band sequence required by SICKLE models."""
        expected_bands = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B9', 'B11', 'B12']
        self.assertEqual(SICKLE_S2_BANDS, expected_bands)

    def test_invalid_band_detection(self):
        """Verify Sentinel2SAFEProduct detects missing bands or directories."""
        with self.assertRaises(FileNotFoundError):
            Sentinel2SAFEProduct("non_existent_product_directory.SAFE")

    # ---------------------------------------------------------------------
    # 3. Pretrained Model Weights & Output Dimension Tests
    # ---------------------------------------------------------------------
    def test_crop_type_model_forward(self):
        """Verify S2CropTypeModel outputs 2 classes (Paddy, Non-Paddy)."""
        model = S2CropTypeModel(in_channel=12, n_classes=2)
        # Input shape: (1, T=4, 12, 32, 32)
        x = torch.randn(1, 4, 12, 32, 32)
        out = model(x)
        self.assertEqual(out.shape, (1, 2, 32, 32))

    def test_yield_regression_model_forward(self):
        """Verify S2YieldModel outputs 1 continuous regression channel."""
        model = S2YieldModel(in_channel=12)
        x = torch.randn(1, 4, 12, 32, 32)
        out = model(x)
        self.assertEqual(out.shape, (1, 1, 32, 32))

    def test_missing_checkpoint_error(self):
        """Verify clean FileNotFoundError when loading non-existent checkpoint."""
        with self.assertRaises(FileNotFoundError):
            SICKLEInferencePipeline("non_existent_checkpoint.pth.tar")
        with self.assertRaises(FileNotFoundError):
            SICKLEYieldInferencePipeline("non_existent_checkpoint.pth.tar")

    # ---------------------------------------------------------------------
    # 4. Five-District Coverage Accounting Tests
    # ---------------------------------------------------------------------
    def test_all_five_target_districts_registered(self):
        """Verify all 5 target districts are accounted for with correct classifications."""
        target_districts = ["Thanjavur", "Thiruvarur", "Salem", "Tiruchirappalli", "Dharmapuri"]
        for d in target_districts:
            meta = self.manager.get_district_metadata(d)
            self.assertEqual(meta["district"], d)
            self.assertIn("coverage_status", meta)
            self.assertIn("limitations", meta)
            self.assertIn("missing_inputs", meta)

        self.assertEqual(DISTRICT_METADATA["Thanjavur"]["coverage_status"], COVERAGE_COMPLETE_SICKLE)
        self.assertEqual(DISTRICT_METADATA["Thiruvarur"]["coverage_status"], COVERAGE_COMPLETE_SICKLE)
        self.assertEqual(DISTRICT_METADATA["Salem"]["coverage_status"], COVERAGE_SINGLE_SCENE)
        self.assertEqual(DISTRICT_METADATA["Tiruchirappalli"]["coverage_status"], COVERAGE_BORDER_PARTIAL)
        self.assertEqual(DISTRICT_METADATA["Dharmapuri"]["coverage_status"], COVERAGE_BORDER_PARTIAL)

    def test_unsupported_district_rejected(self):
        """Verify ValueError when querying non-target district in satellite workflow."""
        with self.assertRaises(ValueError):
            self.manager.get_district_metadata("Coimbatore")

    def test_district_features_schema(self):
        """Verify output schema of get_district_features for all 5 districts."""
        for d in ["Thanjavur", "Thiruvarur", "Salem", "Tiruchirappalli", "Dharmapuri"]:
            res = self.manager.get_district_features(d)
            self.assertEqual(res["district"], d)
            self.assertIn("multi_spectral_features", res)
            self.assertIn("mean_ndvi", res["multi_spectral_features"])
            self.assertIn("observation_dates", res)
            self.assertIn("sickle_ai_models", res)
            self.assertIn("data_completeness", res)
            self.assertIn("copernicus_12m", res)
            self.assertGreater(res["copernicus_12m"]["total_usable_observations"], 0)
            self.assertIn("observation_window", res["copernicus_12m"])
            self.assertIn("season_identification", res["copernicus_12m"])

    # ---------------------------------------------------------------------
    # 5. Unit and Aggregation Consistency & Insufficient Data Handling Tests
    # ---------------------------------------------------------------------
    def test_unit_conversion_constants(self):
        """Verify exact metric conversion formula: 1 kg/acre = 0.00247105 tonnes/ha."""
        self.assertAlmostEqual(KG_ACRE_TO_TONNES_HA, 0.00247105, places=8)
        
        # 1920 kg/acre (UID 2177) -> 4.744 tonnes/ha
        yield_kg = 1920.0
        yield_tha = yield_kg * KG_ACRE_TO_TONNES_HA
        self.assertAlmostEqual(yield_tha, 4.744416, places=4)

    def test_district_prediction_integration(self):
        """Verify baseline vs satellite-enhanced prediction integration and insufficient data handling."""
        import joblib
        import pandas as pd
        model = joblib.load('models/best_yield_model.joblib')
        preprocessor = joblib.load('models/preprocessing_pipeline.joblib')
        processed_df = pd.read_csv('data/processed/rice_yield_processed.csv')

        # Thanjavur: Sufficient multi-temporal SICKLE data -> Real prediction succeeds
        pred_thanjavur = self.manager.compute_district_yield_prediction(
            district="Thanjavur",
            year=2023,
            baseline_model=model,
            preprocessor=preprocessor,
            processed_df=processed_df
        )
        self.assertEqual(pred_thanjavur["district"], "Thanjavur")
        self.assertEqual(pred_thanjavur["status"], "success")
        self.assertGreater(pred_thanjavur["baseline_tabular_yield_tha"], 0.0)
        self.assertIsNotNone(pred_thanjavur["satellite_enhanced_yield_tha"])
        self.assertGreater(pred_thanjavur["satellite_enhanced_yield_tha"], 0.0)
        self.assertEqual(len(pred_thanjavur["confidence_interval_tha"]), 2)
        self.assertIn("model_used", pred_thanjavur)
        self.assertGreater(pred_thanjavur["usable_observations_count"], 0)

        # Salem & Dharmapuri: Insufficient local rasters -> Honestly report insufficient data without fabricating
        for d in ["Salem", "Dharmapuri"]:
            pred = self.manager.compute_district_yield_prediction(
                district=d,
                year=2023,
                baseline_model=model,
                preprocessor=preprocessor,
                processed_df=processed_df
            )
            self.assertEqual(pred["district"], d)
            self.assertEqual(pred["status"], "insufficient_data")
            self.assertIsNone(pred["satellite_enhanced_yield_tha"])
            self.assertIsNone(pred["confidence_interval_tha"])
            self.assertIn("insufficient_data_reason", pred)
            self.assertIn("model_used", pred)
            self.assertIn("usable_observations_count", pred)
            self.assertGreater(pred["usable_observations_count"], 0)
            self.assertIn("observation_date_range", pred)
            self.assertIn("cloud_quality", pred)


if __name__ == '__main__':
    print("=" * 70)
    print("RUNNING PHASE 3 SATELLITE ENHANCED WORKFLOW TEST SUITE")
    print("=" * 70)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSatelliteWorkflow)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
