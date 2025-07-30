import pytest


def test_dataset_upload():
    """測試是否可以成功上傳資料集到 Hugging Face"""
    from datasets import load_dataset
    from tw_textforge.config.settings import setting
    
    dataset = load_dataset("csv", data_files="data/TW-TextForge-TestCSVUpload-data.csv", verification_mode="no_checks",)
    
    try:
        dataset.push_to_hub("TsukiOwO/TW-TextForge-TestCSVUpload", token=setting.hf_token, private=False)
        assert True, "資料集上傳成功"
    except Exception as e:
        pytest.fail(f"上傳資料集失敗: {e}")
        assert False, f"上傳資料集失敗: {e}"

if __name__ == "__main__":
    pytest.main([__file__])