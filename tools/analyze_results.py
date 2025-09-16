#!/usr/bin/env python3
import re
import csv
import sys
import os
from typing import Dict, List, Tuple
import argparse
from datetime import datetime

try:
    import matplotlib.pyplot as plt
    import numpy as np
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

class RealTimeAnalyzer:
    def __init__(self):
        self.test_cases = [
            "Pure Computation",
            "Regular Branch Pattern", 
            "Pseudo-Random Branch Pattern",
            "Nested Branch Pattern",
            "Memory + Branch Mixed",
            "High-Frequency Branches"
        ]
        self.results = {}
        self.cpu_model = self._get_cpu_model()
    
    def _get_cpu_model(self) -> str:
        """获取CPU型号信息"""
        try:
            # 尝试从 /proc/cpuinfo 读取CPU信息
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if line.startswith('model name'):
                        # 提取CPU型号名称
                        cpu_name = line.split(':', 1)[1].strip()
                        # 简化CPU名称，移除多余信息
                        cpu_name = cpu_name.replace('(R)', '').replace('(TM)', '')
                        cpu_name = ' '.join(cpu_name.split())  # 移除多余空格
                        return cpu_name
        except (FileNotFoundError, PermissionError, IndexError):
            pass
        
        # 如果无法读取 /proc/cpuinfo，尝试其他方法
        try:
            import subprocess
            result = subprocess.run(['lscpu'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'Model name:' in line:
                        cpu_name = line.split(':', 1)[1].strip()
                        cpu_name = cpu_name.replace('(R)', '').replace('(TM)', '')
                        cpu_name = ' '.join(cpu_name.split())
                        return cpu_name
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        # 默认返回值
        return "Unknown CPU"
        
    def parse_benchmark_output(self, filename: str) -> Dict:
        """Parse benchmark output file"""
        with open(filename, 'r') as f:
            content = f.read()
        
        results = {}
        
        # 正则表达式匹配模式
        pattern = r'=== (.+?) ===\s+Min: (\d+), Max: (\d+), Avg: (\d+)\s+Jitter: (\d+), Std Dev: ([\d.]+)\s+95th percentile: (\d+), 99th percentile: (\d+)\s+Coefficient of Variation: ([\d.]+)'
        
        matches = re.findall(pattern, content)
        
        for match in matches:
            test_name = match[0]
            results[test_name] = {
                'min': int(match[1]),
                'max': int(match[2]),
                'avg': int(match[3]),
                'jitter': int(match[4]),
                'std_dev': float(match[5]),
                'p95': int(match[6]),
                'p99': int(match[7]),
                'cv': float(match[8])
            }
        
        self.results = results
        return results
    
    def calculate_realtime_scores(self) -> Dict:
        """计算量化的实时性评分"""
        scores = {}
        
        # 收集所有指标用于归一化
        all_jitters = [data['jitter'] for data in self.results.values()]
        all_std_devs = [data['std_dev'] for data in self.results.values()]
        all_cvs = [data['cv'] for data in self.results.values()]
        all_max_avg_ratios = [data['max'] / data['avg'] for data in self.results.values()]
        all_p99_avg_ratios = [data['p99'] / data['avg'] for data in self.results.values()]
        
        # 计算归一化参数
        max_jitter = max(all_jitters)
        max_std_dev = max(all_std_devs)
        max_cv = max(all_cvs)
        max_ratio = max(all_max_avg_ratios)
        max_p99_ratio = max(all_p99_avg_ratios)
        
        for test_name, data in self.results.items():
            # 1. 抖动评分 (0-100, 越高越好)
            jitter_score = max(0, 100 * (1 - data['jitter'] / max_jitter))
            
            # 2. 标准差评分 (0-100, 越高越好)
            std_dev_score = max(0, 100 * (1 - data['std_dev'] / max_std_dev))
            
            # 3. 变异系数评分 (0-100, 越高越好)
            cv_score = max(0, 100 * (1 - data['cv'] / max_cv))
            
            # 4. 最大值/平均值比值评分 (0-100, 越高越好)
            max_avg_ratio = data['max'] / data['avg']
            ratio_score = max(0, 100 * (1 - max_avg_ratio / max_ratio))
            
            # 5. 99th分位数/平均值比值评分 (0-100, 越高越好)
            p99_avg_ratio = data['p99'] / data['avg']
            p99_score = max(0, 100 * (1 - p99_avg_ratio / max_p99_ratio))
            
            # 6. 综合实时性评分 (加权平均)
            weights = {
                'jitter': 0.2,
                'std_dev': 0.2, 
                'cv': 0.25,
                'ratio': 0.15,
                'p99': 0.2
            }
            
            overall_score = (
                weights['jitter'] * jitter_score +
                weights['std_dev'] * std_dev_score +
                weights['cv'] * cv_score +
                weights['ratio'] * ratio_score +
                weights['p99'] * p99_score
            )
            
            # 7. 实时性等级评定
            if overall_score >= 90:
                rt_grade = "Excellent"
            elif overall_score >= 75:
                rt_grade = "Good"
            elif overall_score >= 60:
                rt_grade = "Fair"
            elif overall_score >= 40:
                rt_grade = "Poor"
            else:
                rt_grade = "Very Poor"
            
            scores[test_name] = {
                'jitter_score': round(jitter_score, 2),
                'std_dev_score': round(std_dev_score, 2),
                'cv_score': round(cv_score, 2),
                'ratio_score': round(ratio_score, 2),
                'p99_score': round(p99_score, 2),
                'overall_score': round(overall_score, 2),
                'rt_grade': rt_grade,
                'max_avg_ratio': round(max_avg_ratio, 3),
                'p99_avg_ratio': round(p99_avg_ratio, 3)
            }
            
        return scores
    
    def export_to_csv(self, output_file: str, experiment_dir: str = None):
        scores = self.calculate_realtime_scores()
        
        # 如果指定了实验目录，将CSV文件也保存到该目录
        if experiment_dir:
            filename = os.path.basename(output_file)
            output_file = os.path.join(experiment_dir, filename)
        
        # 准备CSV数据
        headers = [
            'Test_Case',
            'Min_Cycles', 'Max_Cycles', 'Avg_Cycles',
            'Jitter_Cycles', 'Std_Dev', 'CV',
            'P95_Cycles', 'P99_Cycles',
            'Max_Avg_Ratio', 'P99_Avg_Ratio',
            'Jitter_Score', 'StdDev_Score', 'CV_Score',
            'Ratio_Score', 'P99_Score', 'Overall_RT_Score',
            'RT_Grade'
        ]
        
        rows = []
        for test_name in self.test_cases:
            if test_name in self.results:
                data = self.results[test_name]
                score = scores[test_name]
                
                row = [
                    test_name,
                    data['min'], data['max'], data['avg'],
                    data['jitter'], data['std_dev'], data['cv'],
                    data['p95'], data['p99'],
                    score['max_avg_ratio'], score['p99_avg_ratio'],
                    score['jitter_score'], score['std_dev_score'], score['cv_score'],
                    score['ratio_score'], score['p99_score'], score['overall_score'],
                    score['rt_grade']
                ]
                rows.append(row)
        
        # 写入CSV文件
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        
        print(f"✓ Result exported to: {output_file}")
        return output_file
    
    def print_summary(self):
        """打印分析摘要"""
        scores = self.calculate_realtime_scores()
        
        print("\n" + "="*80)
        print("              Real-time analysis summary")
        print("="*80)
        
        # 按综合评分排序
        sorted_tests = sorted(scores.items(), key=lambda x: x[1]['overall_score'], reverse=True)
        
        print(f"{'Rank':<4} {'Test Case':<25} {'Overall Score':<10} {'Grade':<12} {'CV':<10}")
        print("-" * 80)
        
        for i, (test_name, score) in enumerate(sorted_tests, 1):
            cv = self.results[test_name]['cv']
            print(f"{i:<4} {test_name:<25} {score['overall_score']:<10.1f} {score['rt_grade']:<12} {cv:<10.4f}")
        
        # print("\nScore explanation:")
        # print("- Overall score: 0-100, better score is better")
        # print("- Score based on: Jitter, Std Dev, CV, Max Ratio, 99th Percentile Ratio")
        # print("- Grade: Excellent(90+), Good(75+), Fair(60+), Poor(40+), Very Poor(<40)")
    
    def create_visualization(self, output_dir: str = "."):
        """创建可视化图表"""
        if not HAS_MATPLOTLIB:
            raise ImportError("matplotlib not installed, cannot generate visualization chart")
            
        scores = self.calculate_realtime_scores()
        
        # 设置Arial绘图
        plt.rcParams['font.family'] = 'Arial'
        plt.rcParams['font.size'] = 14
        plt.rcParams['axes.labelsize'] = 16
        plt.rcParams['axes.titlesize'] = 18
        plt.rcParams['xtick.labelsize'] = 14
        plt.rcParams['ytick.labelsize'] = 14
        plt.rcParams['legend.fontsize'] = 14
        plt.rcParams['figure.titlesize'] = 20
        
        # 创建子图
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(f'MicroBench on {self.cpu_model}', fontsize=20, fontweight='bold')
        
        test_names = [name.replace(' ', '\n') for name in self.test_cases if name in self.results]
        
        # 1. 综合实时性评分对比
        overall_scores = [scores[name]['overall_score'] for name in self.test_cases if name in scores]
        bars1 = ax1.bar(range(len(test_names)), overall_scores, color='skyblue', edgecolor='navy', linewidth=1)
        ax1.set_title('Overall Real-time Score Comparison', fontsize=18, fontweight='bold', pad=20)
        ax1.set_ylabel('Score (0-100)', fontsize=16, fontweight='bold')
        ax1.set_xticks(range(len(test_names)))
        ax1.set_xticklabels(test_names, rotation=45, ha='right', fontsize=12, fontweight='bold')
        ax1.tick_params(axis='y', labelsize=14)
        ax1.grid(True, alpha=0.3)
        
        # 添加数值标签
        for bar, score in zip(bars1, overall_scores):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f'{score:.1f}', ha='center', va='bottom', fontsize=14, fontweight='bold')
        
        # 2. 变异系数对比
        cvs = [self.results[name]['cv'] for name in self.test_cases if name in self.results]
        bars2 = ax2.bar(range(len(test_names)), cvs, color='lightcoral', edgecolor='darkred', linewidth=1)
        ax2.set_title('Coefficient of Variation (Lower is Better)', fontsize=18, fontweight='bold', pad=20)
        ax2.set_ylabel('CV', fontsize=16, fontweight='bold')
        ax2.set_xticks(range(len(test_names)))
        ax2.set_xticklabels(test_names, rotation=45, ha='right', fontsize=12, fontweight='bold')
        ax2.tick_params(axis='y', labelsize=14)
        ax2.grid(True, alpha=0.3)
        
        # 添加数值标签
        for bar, cv in zip(bars2, cvs):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(cvs)*0.02,
                    f'{cv:.4f}', ha='center', va='bottom', fontsize=14, fontweight='bold')
        
        # 3. 抖动对比
        jitters = [self.results[name]['jitter'] for name in self.test_cases if name in self.results]
        bars3 = ax3.bar(range(len(test_names)), jitters, color='lightgreen', edgecolor='darkgreen', linewidth=1)
        ax3.set_title('Jitter (Max - Min) in CPU Cycles', fontsize=18, fontweight='bold', pad=20)
        ax3.set_ylabel('Cycles', fontsize=16, fontweight='bold')
        ax3.set_xticks(range(len(test_names)))
        ax3.set_xticklabels(test_names, rotation=45, ha='right', fontsize=12, fontweight='bold')
        ax3.tick_params(axis='y', labelsize=14)
        ax3.grid(True, alpha=0.3)
        
        # 添加数值标签
        for bar, jitter in zip(bars3, jitters):
            ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(jitters)*0.02,
                    f'{jitter}', ha='center', va='bottom', fontsize=14, fontweight='bold')
        
        # 4. 99th分位数/平均值比例
        p99_ratios = [scores[name]['p99_avg_ratio'] for name in self.test_cases if name in scores]
        bars4 = ax4.bar(range(len(test_names)), p99_ratios, color='orange', edgecolor='darkorange', linewidth=1)
        ax4.set_title('99th Percentile / Average Ratio', fontsize=18, fontweight='bold', pad=20)
        ax4.set_ylabel('Ratio', fontsize=16, fontweight='bold')
        ax4.set_xticks(range(len(test_names)))
        ax4.set_xticklabels(test_names, rotation=45, ha='right', fontsize=12, fontweight='bold')
        ax4.tick_params(axis='y', labelsize=14)
        ax4.grid(True, alpha=0.3)
        
        # 添加数值标签
        for bar, ratio in zip(bars4, p99_ratios):
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(p99_ratios)*0.02,
                    f'{ratio:.3f}', ha='center', va='bottom', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        # 保存图表到指定的实验目录
        if output_dir:
            # 直接使用传入的实验目录
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = os.path.join(output_dir, f"rt_analysis_{timestamp}.png")
        else:
            # 如果没有指定目录，使用默认路径
            output_dir = "../result"
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = os.path.join(output_dir, f"rt_analysis_{timestamp}.png")
        
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Visualization chart saved to: {output_file}")
        
        return output_file

class MultiRunAnalyzer:
    def __init__(self):
        self.test_cases = [
            "Pure Computation",
            "Regular Branch Pattern", 
            "Pseudo-Random Branch Pattern",
            "Nested Branch Pattern",
            "Memory + Branch Mixed",
            "High-Frequency Branches"
        ]
        self.all_runs_data = []  # 存储所有运行的数据
        self.statistics = {}     # 存储统计数据
        self.cpu_model = self._get_cpu_model()
    
    def _get_cpu_model(self) -> str:
        """获取CPU型号信息"""
        try:
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if line.startswith('model name'):
                        cpu_name = line.split(':', 1)[1].strip()
                        cpu_name = cpu_name.replace('(R)', '').replace('(TM)', '')
                        cpu_name = ' '.join(cpu_name.split())
                        return cpu_name
        except (FileNotFoundError, PermissionError, IndexError):
            pass
        
        try:
            import subprocess
            result = subprocess.run(['lscpu'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'Model name:' in line:
                        cpu_name = line.split(':', 1)[1].strip()
                        cpu_name = cpu_name.replace('(R)', '').replace('(TM)', '')
                        cpu_name = ' '.join(cpu_name.split())
                        return cpu_name
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        return "Unknown CPU"
    
    def analyze_multi_runs(self, multi_run_dir: str) -> Dict:
        """分析多次运行的结果"""
        import glob
        
        # 查找所有运行结果文件
        result_files = glob.glob(os.path.join(multi_run_dir, "run_*.txt"))
        
        if not result_files:
            raise FileNotFoundError(f"No run result files found in {multi_run_dir}")
        
        result_files.sort()  # 按文件名排序
        print(f"Found {len(result_files)} run result files")
        
        # 分析每个运行结果
        for i, file_path in enumerate(result_files, 1):
            print(f"Analyzing run {i}/{len(result_files)}: {os.path.basename(file_path)}")
            
            analyzer = RealTimeAnalyzer()
            try:
                results = analyzer.parse_benchmark_output(file_path)
                if results:
                    self.all_runs_data.append(results)
                else:
                    print(f"Warning: Failed to parse {file_path}")
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")
        
        if not self.all_runs_data:
            raise ValueError("No valid run data found")
        
        print(f"Successfully analyzed {len(self.all_runs_data)} runs")
        
        # 计算统计数据
        self._calculate_statistics()
        return self.statistics
    
    def _calculate_statistics(self):
        """计算多次运行的统计数据"""
        import numpy as np
        
        # 为每个测试用例计算统计数据
        for test_case in self.test_cases:
            if test_case not in self.all_runs_data[0]:
                continue
            
            # 收集该测试用例在所有运行中的数据
            metrics = ['min', 'max', 'avg', 'jitter', 'std_dev', 'p95', 'p99', 'cv']
            test_stats = {}
            
            for metric in metrics:
                values = []
                for run_data in self.all_runs_data:
                    if test_case in run_data and metric in run_data[test_case]:
                        values.append(run_data[test_case][metric])
                
                if values:
                    test_stats[metric] = {
                        'mean': np.mean(values),
                        'std': np.std(values),
                        'min': np.min(values),
                        'max': np.max(values),
                        'median': np.median(values),
                        'q25': np.percentile(values, 25),
                        'q75': np.percentile(values, 75),
                        'count': len(values),
                        'raw_values': values
                    }
                    
                    # 计算95%置信区间
                    if len(values) > 1:
                        try:
                            from scipy import stats
                            confidence = 0.95
                            alpha = 1 - confidence
                            dof = len(values) - 1
                            t_critical = stats.t.ppf(1 - alpha/2, dof)
                            margin_error = t_critical * (test_stats[metric]['std'] / np.sqrt(len(values)))
                            test_stats[metric]['ci_lower'] = test_stats[metric]['mean'] - margin_error
                            test_stats[metric]['ci_upper'] = test_stats[metric]['mean'] + margin_error
                        except ImportError:
                            # 如果没有scipy，使用简单的估算（正态分布近似）
                            margin_error = 1.96 * (test_stats[metric]['std'] / np.sqrt(len(values)))
                            test_stats[metric]['ci_lower'] = test_stats[metric]['mean'] - margin_error
                            test_stats[metric]['ci_upper'] = test_stats[metric]['mean'] + margin_error
            
            self.statistics[test_case] = test_stats
    
    def export_statistics_to_csv(self, output_file: str, output_dir: str = None):
        """导出统计数据到CSV"""
        if output_dir:
            filename = os.path.basename(output_file)
            output_file = os.path.join(output_dir, filename)
        
        headers = [
            'Test_Case', 'Metric',
            'Mean', 'Std_Dev', 'Min', 'Max', 'Median',
            'Q25', 'Q75', 'CI_Lower', 'CI_Upper', 'Sample_Count',
            'Coefficient_of_Variation'
        ]
        
        rows = []
        for test_case in self.test_cases:
            if test_case not in self.statistics:
                continue
            
            for metric, stats in self.statistics[test_case].items():
                # 计算变异系数
                cv = stats['std'] / stats['mean'] if stats['mean'] != 0 else 0
                
                row = [
                    test_case, metric,
                    round(stats['mean'], 4),
                    round(stats['std'], 4),
                    round(stats['min'], 4),
                    round(stats['max'], 4),
                    round(stats['median'], 4),
                    round(stats['q25'], 4),
                    round(stats['q75'], 4),
                    round(stats.get('ci_lower', 0), 4),
                    round(stats.get('ci_upper', 0), 4),
                    stats['count'],
                    round(cv, 6)
                ]
                rows.append(row)
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        
        print(f"✓ Multi-run statistics exported to: {output_file}")
        return output_file
    
    def create_statistical_visualization(self, output_dir: str = "."):
        """创建统计可视化图表"""
        if not HAS_MATPLOTLIB:
            raise ImportError("matplotlib not installed, cannot generate visualization chart")
        
        import numpy as np
        
        # 设置字体
        plt.rcParams['font.family'] = 'DejaVu Sans'  # 使用系统默认字体
        plt.rcParams['font.size'] = 12
        plt.rcParams['axes.labelsize'] = 14
        plt.rcParams['axes.titlesize'] = 16
        plt.rcParams['xtick.labelsize'] = 12
        plt.rcParams['ytick.labelsize'] = 12
        plt.rcParams['legend.fontsize'] = 12
        plt.rcParams['figure.titlesize'] = 18
        
        # 创建子图
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(f'MicroBench Multi-Run Statistical Analysis on {self.cpu_model}', fontsize=18, fontweight='bold')
        
        test_names = [name.replace(' ', '\n') for name in self.test_cases if name in self.statistics]
        
        # 1. 平均执行时间及置信区间
        avg_means = []
        avg_cis_lower = []
        avg_cis_upper = []
        
        for test_case in self.test_cases:
            if test_case in self.statistics and 'avg' in self.statistics[test_case]:
                stats = self.statistics[test_case]['avg']
                avg_means.append(stats['mean'])
                avg_cis_lower.append(stats.get('ci_lower', stats['mean']))
                avg_cis_upper.append(stats.get('ci_upper', stats['mean']))
            else:
                avg_means.append(0)
                avg_cis_lower.append(0)
                avg_cis_upper.append(0)
        
        x_pos = range(len(test_names))
        bars1 = ax1.bar(x_pos, avg_means, color='skyblue', edgecolor='navy', linewidth=1, alpha=0.7)
        
        # 添加误差线（置信区间）
        yerr_lower = [avg_means[i] - avg_cis_lower[i] for i in range(len(avg_means))]
        yerr_upper = [avg_cis_upper[i] - avg_means[i] for i in range(len(avg_means))]
        ax1.errorbar(x_pos, avg_means, yerr=[yerr_lower, yerr_upper], 
                    fmt='none', color='red', capsize=5, capthick=2)
        
        ax1.set_title(f'Average Execution Time with 95% CI\n({len(self.all_runs_data)} runs)', fontweight='bold')
        ax1.set_ylabel('CPU Cycles', fontweight='bold')
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(test_names, rotation=45, ha='right', fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # 2. 变异系数的分布
        cv_means = []
        cv_stds = []
        
        for test_case in self.test_cases:
            if test_case in self.statistics and 'cv' in self.statistics[test_case]:
                stats = self.statistics[test_case]['cv']
                cv_means.append(stats['mean'])
                cv_stds.append(stats['std'])
            else:
                cv_means.append(0)
                cv_stds.append(0)
        
        bars2 = ax2.bar(x_pos, cv_means, yerr=cv_stds, color='lightcoral', 
                       edgecolor='darkred', linewidth=1, alpha=0.7, capsize=5)
        ax2.set_title('Coefficient of Variation (Lower is Better)', fontweight='bold')
        ax2.set_ylabel('CV', fontweight='bold')
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels(test_names, rotation=45, ha='right', fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        # 3. 最大 Jitter 和 Jitter 稳定性
        max_jitters = []
        jitter_cvs = []
        
        for test_case in self.test_cases:
            if test_case in self.statistics and 'jitter' in self.statistics[test_case]:
                stats = self.statistics[test_case]['jitter']
                # 最大 jitter：所有运行中的最坏情况
                max_jitters.append(stats['max'])
                # Jitter 的变异系数：衡量 jitter 的一致性
                jitter_cv = stats['std'] / stats['mean'] if stats['mean'] != 0 else 0
                jitter_cvs.append(jitter_cv)
            else:
                max_jitters.append(0)
                jitter_cvs.append(0)
        
        # 使用双Y轴显示最大jitter和jitter稳定性
        ax3_twin = ax3.twinx()
        
        # 主轴：最大 jitter (柱状图)
        bars3 = ax3.bar(x_pos, max_jitters, color='lightgreen', 
                       edgecolor='darkgreen', linewidth=1, alpha=0.7, width=0.6)
        ax3.set_title('Maximum Jitter & Jitter Consistency', fontweight='bold')
        ax3.set_ylabel('Max Jitter (CPU Cycles)', fontweight='bold', color='darkgreen')
        ax3.set_xticks(x_pos)
        ax3.set_xticklabels(test_names, rotation=45, ha='right', fontweight='bold')
        ax3.grid(True, alpha=0.3)
        ax3.tick_params(axis='y', labelcolor='darkgreen')
        
        # 次轴：jitter 变异系数 (折线图)
        line3 = ax3_twin.plot(x_pos, jitter_cvs, color='red', marker='o', 
                             linewidth=2, markersize=6, label='Jitter CV')
        ax3_twin.set_ylabel('Jitter CV (Lower is Better)', fontweight='bold', color='red')
        ax3_twin.tick_params(axis='y', labelcolor='red')
        
        # 添加数值标签
        for i, (max_jit, cv) in enumerate(zip(max_jitters, jitter_cvs)):
            # 最大 jitter 标签
            ax3.text(i, max_jit + max(max_jitters)*0.02,
                    f'{max_jit}', ha='center', va='bottom', 
                    fontsize=12, fontweight='bold', color='darkgreen')
            # CV 标签
            ax3_twin.text(i + 0.1, cv + max(jitter_cvs)*0.05,
                         f'{cv:.3f}', ha='left', va='bottom', 
                         fontsize=10, fontweight='bold', color='red')
        
        # 4. 运行之间的一致性（标准差的变异系数）
        consistency_scores = []
        
        for test_case in self.test_cases:
            if test_case in self.statistics and 'avg' in self.statistics[test_case]:
                avg_stats = self.statistics[test_case]['avg']
                # 一致性评分 = 1 / (1 + CV_of_averages)
                cv_of_avg = avg_stats['std'] / avg_stats['mean'] if avg_stats['mean'] != 0 else 1
                consistency = 1 / (1 + cv_of_avg)
                consistency_scores.append(consistency * 100)  # 转换为百分比
            else:
                consistency_scores.append(0)
        
        bars4 = ax4.bar(x_pos, consistency_scores, color='orange', 
                       edgecolor='darkorange', linewidth=1, alpha=0.7)
        ax4.set_title('Cross-Run Consistency Score', fontweight='bold')
        ax4.set_ylabel('Consistency (%)', fontweight='bold')
        ax4.set_xticks(x_pos)
        ax4.set_xticklabels(test_names, rotation=45, ha='right', fontweight='bold')
        ax4.grid(True, alpha=0.3)
        ax4.set_ylim(0, 100)
        
        plt.tight_layout()
        
        # 保存图表
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(output_dir, f"multi_run_analysis_{timestamp}.png")
        
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Multi-run statistical visualization saved to: {output_file}")
        
        return output_file
    
    def print_multi_run_summary(self):
        """打印多次运行的统计摘要"""
        print("\n" + "="*80)
        print(f"    Multi-Run Statistical Analysis Summary ({len(self.all_runs_data)} runs)")
        print("="*80)
        
        print(f"{'Test Case':<25} {'Avg±Std':<15} {'Max Jitter':<12} {'CV':<10} {'Consistency':<12}")
        print("-" * 80)
        
        for test_case in self.test_cases:
            if test_case not in self.statistics:
                continue
            
            avg_stats = self.statistics[test_case].get('avg', {})
            cv_stats = self.statistics[test_case].get('cv', {})
            jitter_stats = self.statistics[test_case].get('jitter', {})
            
            if avg_stats and cv_stats and jitter_stats:
                avg_mean = avg_stats['mean']
                avg_std = avg_stats['std']
                cv_mean = cv_stats['mean']
                max_jitter = jitter_stats['max']  # 最大 jitter
                
                # 计算一致性评分
                cv_of_avg = avg_std / avg_mean if avg_mean != 0 else 1
                consistency = (1 / (1 + cv_of_avg)) * 100
                
                print(f"{test_case:<25} {avg_mean:.0f}±{avg_std:.0f}     {max_jitter:<12.0f} {cv_mean:.4f}    {consistency:.1f}%")

def main():
    parser = argparse.ArgumentParser(description='Analyze MicroBench real-time test results')
    parser.add_argument('input_file', nargs='?', help='benchmark output file path (for single run)')
    parser.add_argument('-o', '--output', default='rt_analysis.csv', help='output CSV file name')
    parser.add_argument('--no-plot', action='store_true', help='do not generate visualization chart')
    parser.add_argument('--multi-run', type=str, help='directory containing multiple run result files')
    
    args = parser.parse_args()
    
    # 检查是多次运行分析还是单次运行分析
    if args.multi_run:
        # 多次运行分析
        if not os.path.exists(args.multi_run):
            print(f"Error: multi-run directory '{args.multi_run}' does not exist")
            sys.exit(1)
        
        print(f"Analyzing multiple runs in directory: {args.multi_run}")
        
        multi_analyzer = MultiRunAnalyzer()
        
        try:
            # 分析多次运行
            statistics = multi_analyzer.analyze_multi_runs(args.multi_run)
            
            if not statistics:
                print("Error: Unable to generate statistics from multi-run data")
                sys.exit(1)
            
            # 导出统计数据到CSV
            csv_output = multi_analyzer.export_statistics_to_csv(args.output, args.multi_run)
            
            # 打印统计摘要
            multi_analyzer.print_multi_run_summary()
            
            # 生成统计可视化图表
            if not args.no_plot:
                try:
                    chart_file = multi_analyzer.create_statistical_visualization(args.multi_run)
                except ImportError:
                    print("Warning: matplotlib not installed, skipping visualization chart generation")
                    print("Install command: pip install matplotlib numpy")
                except Exception as e:
                    print(f"Visualization generation failed: {e}")
            
            print(f"\n✓ Multi-run analysis completed. All files saved to: {args.multi_run}")
            
        except Exception as e:
            print(f"Error occurred during multi-run analysis: {e}")
            sys.exit(1)
    
    else:
        # 单次运行分析（原有逻辑）
        if not args.input_file:
            print("Error: input_file is required for single run analysis")
            print("Use --multi-run for multiple runs analysis or provide input_file for single run")
            sys.exit(1)
        
        if not os.path.exists(args.input_file):
            print(f"Error: input file '{args.input_file}' does not exist")
            sys.exit(1)
        
        analyzer = RealTimeAnalyzer()
        
        try:
            print(f"Analyzing file: {args.input_file}")
            results = analyzer.parse_benchmark_output(args.input_file)
            
            if not results:
                print("Error: Unable to parse valid data from input file")
                sys.exit(1)
            
            print(f"✓ Successfully parsed {len(results)} test cases")
            
            # 创建实验目录
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            date_str = datetime.now().strftime('%Y-%m-%d')
            experiment_dir = os.path.join("../result", f"experiment_{timestamp}")
            os.makedirs(experiment_dir, exist_ok=True)
            
            # 保存原始基准测试结果到实验目录
            original_filename = os.path.basename(args.input_file)
            original_copy = os.path.join(experiment_dir, f"benchmark_raw_{timestamp}.txt")
            import shutil
            shutil.copy2(args.input_file, original_copy)
            
            # 导出CSV到实验目录
            csv_output = analyzer.export_to_csv(args.output, experiment_dir)
            
            # 创建实验信息文件
            info_file = os.path.join(experiment_dir, "experiment_info.txt")
            with open(info_file, 'w') as f:
                f.write(f"MicroBench Real-time Analysis Experiment\n")
                f.write(f"{'='*50}\n")
                f.write(f"Date: {date_str}\n")
                f.write(f"Timestamp: {timestamp}\n")
                f.write(f"Input File: {args.input_file}\n")
                f.write(f"Test Cases: {len(results)}\n")
                f.write(f"Generated Files:\n")
                f.write(f"  - Raw Data: benchmark_raw_{timestamp}.txt\n")
                f.write(f"  - Analysis: {os.path.basename(csv_output)}\n")
                if not args.no_plot:
                    f.write(f"  - Visualization: rt_analysis_{timestamp}.png\n")
                f.write(f"\nExperiment Directory: {experiment_dir}\n")
            
            analyzer.print_summary()
            
            if not args.no_plot:
                try:
                    chart_file = analyzer.create_visualization(experiment_dir)
                except ImportError as e:
                    print("Warning: matplotlib not installed, skipping visualization chart generation")
                    print("Install command: pip install matplotlib")
                except Exception as e:
                    print(f"Visualization generation failed: {e}")
            
            print(f"\n✓ Experiment completed. All files saved to: {experiment_dir}")
            
        except Exception as e:
            print(f"Error occurred during analysis: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
