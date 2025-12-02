import argparse
from sample_extractor import sample_extractor
from realtime_feature_collector import realtime_feature_collector
from train import train_and_evaluate  # 假设训练部分放在 train.py 中

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=str, default="train", help="模式: train / extract / realtime")
    args = parser.parse_args()
    mode = args.mode.lower()

    if mode == "train":
        train_and_evaluate()
    elif mode == "extract":
        sample_extractor()
    elif mode == "realtime":
        realtime_feature_collector()
    else:
        print("❌ 无效模式，请使用 --mode train / extract / realtime")
