import json
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def analyze_threshold_results(base_dir: str = "evaluation_results_model_"):
    """
    Analyze results of different thresholds and generate comparison report.

    Args:
        base_dir: Base name of the result directories.
    """
    # Thresholds to analyze
    #thresholds = ["0.0010", "0.0007", "0.0004", "0.0001"]
    model_name = ["anthropic_claude-3_7-sonnet"]
    # Store results for each threshold
    results = []

    for threshold in model_name:
        dir_path = Path(f"{base_dir}{threshold}")
        if not dir_path.exists():
            print(f"Warning: Directory {dir_path} does not exist, skipping.")
            continue

        # Read result files
        try:
            with open(dir_path / "perfect_matches.json", "r", encoding="utf-8") as f:
                perfect_matches = json.load(f)
            with open(dir_path / "close_matches.json", "r", encoding="utf-8") as f:
                close_matches = json.load(f)
            with open(dir_path / "mid_matches.json", "r", encoding="utf-8") as f:
                mid_matches = json.load(f)
            with open(dir_path / "other_cases.json", "r", encoding="utf-8") as f:
                other_cases = json.load(f)
            with open(dir_path / "error_log.json", "r", encoding="utf-8") as f:
                error_log = json.load(f)

            # Calculate statistics
            total_processed = len(perfect_matches) + len(close_matches) + len(mid_matches) + len(other_cases)
            if total_processed > 0:
                perfect_rate = len(perfect_matches) / total_processed * 100
                close_rate = len(close_matches) / total_processed * 100
                mid_rate = len(mid_matches) / total_processed * 100
                other_rate = len(other_cases) / total_processed * 100
                overall_accuracy = (len(perfect_matches) + len(close_matches) + len(mid_matches)) / total_processed * 100

                results.append({
                    "threshold": threshold,
                    "total_processed": total_processed,
                    "perfect_matches": len(perfect_matches),
                    "close_matches": len(close_matches),
                    "mid_matches": len(mid_matches),
                    "other_cases": len(other_cases),
                    "errors": len(error_log),
                    "perfect_rate": perfect_rate,
                    "close_rate": close_rate,
                    "mid_rate": mid_rate,
                    "other_rate": other_rate,
                    "overall_accuracy": overall_accuracy
                })

                print(f"\n=== Statistics for threshold {threshold} ===")
                print(f"Total processed: {total_processed}")
                print(f"  - Perfect matches: {len(perfect_matches)} ({perfect_rate:.2f}%)")
                print(f"  - Close matches (end frame diff < 10): {len(close_matches)} ({close_rate:.2f}%)")
                print(f"  - Mid matches (10 <= end frame diff < 20): {len(mid_matches)} ({mid_rate:.2f}%)")
                print(f"  - Other cases: {len(other_cases)} ({other_rate:.2f}%)")
                print(f"  - Overall accuracy (perfect+close+mid): {overall_accuracy:.2f}%")
                print(f"  - Error count: {len(error_log)}")

        except Exception as e:
            print(f"Error processing threshold {threshold}: {e}")
            continue

    # Create DataFrame and save as CSV
    if results:
        df = pd.DataFrame(results)
        df.to_csv("threshold_comparison_results.csv", index=False)
        print("\nResults saved to threshold_comparison_results.csv")

        # Visualization
        plt.figure(figsize=(15, 10))

        # 1. Overall accuracy comparison
        plt.subplot(2, 2, 1)
        sns.barplot(data=df, x="threshold", y="overall_accuracy")
        plt.title("Overall Accuracy Comparison for Different Thresholds")
        plt.xlabel("Threshold")
        plt.ylabel("Accuracy (%)")

        # 2. Match type count comparison
        plt.subplot(2, 2, 2)
        df_melt = pd.melt(df, id_vars=["threshold"],
                          value_vars=["perfect_matches", "close_matches", "mid_matches", "other_cases"],
                          var_name="Match Type", value_name="Count")
        sns.barplot(data=df_melt, x="threshold", y="Count", hue="Match Type")
        plt.title("Match Type Distribution for Different Thresholds")
        plt.xlabel("Threshold")
        plt.ylabel("Count")
        plt.legend(title="Match Type")

        # 3. Match type rate comparison
        plt.subplot(2, 2, 3)
        df_melt_rate = pd.melt(df, id_vars=["threshold"],
                               value_vars=["perfect_rate", "close_rate", "mid_rate", "other_rate"],
                               var_name="Match Type", value_name="Rate")
        sns.barplot(data=df_melt_rate, x="threshold", y="Rate", hue="Match Type")
        plt.title("Match Type Rate Distribution for Different Thresholds")
        plt.xlabel("Threshold")
        plt.ylabel("Rate (%)")
        plt.legend(title="Match Type")

        # 4. Error count comparison
        plt.subplot(2, 2, 4)
        sns.barplot(data=df, x="threshold", y="errors")
        plt.title("Error Count Comparison for Different Thresholds")
        plt.xlabel("Threshold")
        plt.ylabel("Error Count")

        plt.tight_layout()
        plt.savefig("threshold_comparison_plots.png")
        print("Visualization saved to threshold_comparison_plots.png")

        # Find best threshold
        best_threshold = df.loc[df["overall_accuracy"].idxmax()]
        print(f"\nBest threshold: {best_threshold['threshold']}")
        print(f"Best accuracy: {best_threshold['overall_accuracy']:.2f}%")

        return df
    else:
        print("No valid result data found.")
        return None

def analyze_model_threshold_combinations(base_dir: str = "eval_end_only_threshold_"):
    """
    分析不同模型和阈值组合的结果并生成比较报告。

    Args:
        base_dir: 结果目录的基础名称。
    """
    # 要分析的阈值和模型
    thresholds = ["0.0010", "0.0007", "0.0004"]
    models = [
        "anthropic_claude-3_7-sonnet",
        "gpt-4o-2024-11-20",
        "gemini-2_5-pro-preview-03-25"
    ]
    
    # 存储每个组合的结果
    results = []

    for threshold in thresholds:
        for model in models:
            dir_path = Path(f"{base_dir}{threshold}_model_{model}")
            if not dir_path.exists():
                print(f"警告：目录 {dir_path} 不存在，跳过。")
                continue

            # 读取结果文件
            try:
                with open(dir_path / "perfect_matches.json", "r", encoding="utf-8") as f:
                    perfect_matches = json.load(f)
                with open(dir_path / "close_matches.json", "r", encoding="utf-8") as f:
                    close_matches = json.load(f)
                with open(dir_path / "mid_matches.json", "r", encoding="utf-8") as f:
                    mid_matches = json.load(f)
                with open(dir_path / "other_cases.json", "r", encoding="utf-8") as f:
                    other_cases = json.load(f)
                with open(dir_path / "error_log.json", "r", encoding="utf-8") as f:
                    error_log = json.load(f)

                # 计算统计信息
                total_processed = len(perfect_matches) + len(close_matches) + len(mid_matches) + len(other_cases)
                if total_processed > 0:
                    perfect_rate = len(perfect_matches) / total_processed * 100
                    close_rate = len(close_matches) / total_processed * 100
                    mid_rate = len(mid_matches) / total_processed * 100
                    other_rate = len(other_cases) / total_processed * 100
                    overall_accuracy = (len(perfect_matches) + len(close_matches) + len(mid_matches)) / total_processed * 100

                    results.append({
                        "threshold": threshold,
                        "model": model,
                        "total_processed": total_processed,
                        "perfect_matches": len(perfect_matches),
                        "close_matches": len(close_matches),
                        "mid_matches": len(mid_matches),
                        "other_cases": len(other_cases),
                        "errors": len(error_log),
                        "perfect_rate": perfect_rate,
                        "close_rate": close_rate,
                        "mid_rate": mid_rate,
                        "other_rate": other_rate,
                        "overall_accuracy": overall_accuracy
                    })

                    print(f"\n=== 阈值 {threshold}, 模型 {model} 的统计信息 ===")
                    print(f"总处理数: {total_processed}")
                    print(f"  - 精确匹配: {len(perfect_matches)} ({perfect_rate:.2f}%)")
                    print(f"  - 接近匹配 (结束帧差异 < 10): {len(close_matches)} ({close_rate:.2f}%)")
                    print(f"  - 中等匹配 (10 <= 结束帧差异 < 20): {len(mid_matches)} ({mid_rate:.2f}%)")
                    print(f"  - 其他情况: {len(other_cases)} ({other_rate:.2f}%)")
                    print(f"  - 综合准确率 (精确+接近+中等): {overall_accuracy:.2f}%")
                    print(f"  - 错误数: {len(error_log)}")

            except Exception as e:
                print(f"处理阈值 {threshold}, 模型 {model} 时出错: {e}")
                continue

    # 创建DataFrame并保存为CSV
    if results:
        df = pd.DataFrame(results)
        df.to_csv("model_threshold_comparison_results.csv", index=False)
        print("\n结果已保存到 model_threshold_comparison_results.csv")

        # 可视化
        plt.figure(figsize=(20, 15))

        # 1. 不同模型和阈值的整体准确率比较
        plt.subplot(2, 2, 1)
        sns.barplot(data=df, x="threshold", y="overall_accuracy", hue="model")
        plt.title("不同模型和阈值的整体准确率比较")
        plt.xlabel("阈值")
        plt.ylabel("准确率 (%)")
        plt.legend(title="模型")

        # 2. 匹配类型数量比较
        plt.subplot(2, 2, 2)
        df_melt = pd.melt(df, id_vars=["threshold", "model"],
                          value_vars=["perfect_matches", "close_matches", "mid_matches", "other_cases"],
                          var_name="匹配类型", value_name="数量")
        sns.barplot(data=df_melt, x="threshold", y="数量", hue="model")
        plt.title("不同模型和阈值的匹配类型分布")
        plt.xlabel("阈值")
        plt.ylabel("数量")
        plt.legend(title="模型")

        # 3. 匹配类型比率比较
        plt.subplot(2, 2, 3)
        df_melt_rate = pd.melt(df, id_vars=["threshold", "model"],
                               value_vars=["perfect_rate", "close_rate", "mid_rate", "other_rate"],
                               var_name="匹配类型", value_name="比率")
        sns.barplot(data=df_melt_rate, x="threshold", y="比率", hue="model")
        plt.title("不同模型和阈值的匹配类型比率分布")
        plt.xlabel("阈值")
        plt.ylabel("比率 (%)")
        plt.legend(title="模型")

        # 4. 错误数量比较
        plt.subplot(2, 2, 4)
        sns.barplot(data=df, x="threshold", y="errors", hue="model")
        plt.title("不同模型和阈值的错误数量比较")
        plt.xlabel("阈值")
        plt.ylabel("错误数量")
        plt.legend(title="模型")

        plt.tight_layout()
        plt.savefig("model_threshold_comparison_plots.png")
        print("可视化结果已保存到 model_threshold_comparison_plots.png")

        # 找出最佳组合
        best_combination = df.loc[df["overall_accuracy"].idxmax()]
        print(f"\n最佳组合:")
        print(f"阈值: {best_combination['threshold']}")
        print(f"模型: {best_combination['model']}")
        print(f"最佳准确率: {best_combination['overall_accuracy']:.2f}%")

        return df
    else:
        print("未找到有效的结果数据。")
        return None

if __name__ == "__main__":
    #analyze_threshold_results()
    analyze_model_threshold_combinations() 