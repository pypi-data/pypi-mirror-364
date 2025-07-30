import os
import statistics
import matplotlib.pyplot as plt
from collections import defaultdict
import matplotlib.cm as cm
import matplotlib.colors as mcolors


class Line_Plot:
    def __init__(self, file_path):
        self.file_path = file_path
        self.flow_data = defaultdict(lambda: {
            "proto": None,
            "sent": 0,
            "received": 0,
            "dropped": 0,
            "send_time": {},
            "receive_time": {},
            "sizes": [],
            "delays": [],
            "delay_trace": [],
            "inter_arrival": [],
            "throughput_trace": [],
            "recv_time_series": [],
            "last_recv_time": None
        })

    def parse(self):
        with open(self.file_path, 'r') as file:
            for line in file:
                if not line.strip():
                    continue

                parts = line.strip().split()
                if len(parts) < 11:
                    continue

                event = parts[0]
                time = float(parts[1])
                src = parts[2]
                dst = parts[3]
                pkt_type = parts[4]
                pkt_size = int(parts[5])
                flow_id = parts[7]
                seq_no = parts[10]

                flow = self.flow_data[flow_id]
                flow["proto"] = pkt_type

                if event == "+" and src == "0":
                    flow["sent"] += 1
                    flow["send_time"][seq_no] = time

                elif event == "r" and dst == "1":
                    flow["received"] += 1
                    flow["receive_time"][seq_no] = time
                    flow["sizes"].append(pkt_size)
                    flow["recv_time_series"].append((time, flow["received"]))

                    if flow["last_recv_time"] is not None:
                        inter = time - flow["last_recv_time"]
                        flow["inter_arrival"].append((time, inter))

                    flow["last_recv_time"] = time

                    if seq_no in flow["send_time"]:
                        delay = time - flow["send_time"][seq_no]
                        flow["delays"].append(delay)
                        flow["delay_trace"].append((time, delay))
                        flow["throughput_trace"].append((time, pkt_size * 8 / 1000))  # kbps

                elif event == "d":
                    flow["dropped"] += 1

    def compute(self):
        self.stats = {}
        for fid, data in self.flow_data.items():
            sent = data["sent"]
            recv = data["received"]
            delays = data["delays"]
            duration = (
                max(data["receive_time"].values()) - min(data["receive_time"].values())
                if data["receive_time"] else 1
            )
            total_bits = sum(data["sizes"]) * 8

            self.stats[fid] = {
                "Protocol": data["proto"],
                "Packets Sent": sent,
                "Packets Received": recv,
                "Packets Dropped": data["dropped"],
                "PDR": round(recv / sent, 3) if sent else 0.0,
                "Avg Delay (s)": round(sum(delays) / len(delays), 6) if delays else 0.0,
                "Jitter (s)": round(statistics.stdev(delays), 6) if len(delays) > 1 else 0.0,
                "Throughput (kbps)": round((total_bits / duration) / 1000, 3) if duration else 0.0
            }

    def get_stats(self):
        return self.stats

    def print_summary(self):
        print(f"\n{'Flow':<6} {'Proto':<6} {'Sent':<6} {'Recv':<6} {'Drop':<6} {'PDR':<6} {'AvgDelay(s)':<14} {'Jitter(s)':<12} {'Throughput(kbps)':<16}")
        for fid, s in self.stats.items():
            print(f"{fid:<6} {s['Protocol']:<6} {s['Packets Sent']:<6} {s['Packets Received']:<6} {s['Packets Dropped']:<6} "
                  f"{s['PDR']:<6} {s['Avg Delay (s)']:<14} {s['Jitter (s)']:<12} {s['Throughput (kbps)']:<16}")

    def plot_table(self, output_file="flowstats.png"):
        if not self.stats:
            print("No stats computed. Call compute() first.")
            return

        flows = list(self.stats.keys())
        col_labels = ["Proto", "Sent", "Recv", "Drop", "PDR", "Delay", "Jitter", "Thru (kbps)"]
        table_data = [
            [
                self.stats[f]["Protocol"],
                self.stats[f]["Packets Sent"],
                self.stats[f]["Packets Received"],
                self.stats[f]["Packets Dropped"],
                self.stats[f]["PDR"],
                self.stats[f]["Avg Delay (s)"],
                self.stats[f]["Jitter (s)"],
                self.stats[f]["Throughput (kbps)"]
            ]
            for f in flows
        ]

        fig, ax = plt.subplots(figsize=(12, 0.6 * len(flows) + 2))
        ax.axis("off")
        table = ax.table(
            cellText=table_data,
            colLabels=col_labels,
            rowLabels=flows,
            loc="center",
            cellLoc="center"
        )
        table.scale(1, 1.5)
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        plt.title("Flow Statistics Table", fontsize=14)
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Saved flow stats table to: {output_file}")

    def plot_all_metrics(self, output_file="all_metrics.png"):
        self.parse()
        self.compute()
        self.print_summary()
        
        metrics = {
            "End-to-End Delay (s)": "delay_trace",
            "Inter-packet Delay (s)": "inter_arrival",
            "Throughput (kbps)": "throughput_trace",
            "Cumulative Received Packets": "recv_time_series"
        }

        num_metrics = len(metrics)
        fig, axs = plt.subplots(num_metrics, 1, figsize=(12, 3 * num_metrics), sharex=True)
        fig.suptitle("Per-Packet Flow Metrics", fontsize=16)

        colors = list(cm.get_cmap("tab10").colors)
        flow_ids = list(self.flow_data.keys())

        for ax, (title, key) in zip(axs, metrics.items()):
            for i, fid in enumerate(flow_ids):
                data = self.flow_data[fid]
                series = sorted(data[key])
                if not series:
                    continue
                times = [pt[0] for pt in series]
                values = [pt[1] for pt in series]
                color = colors[i % len(colors)]
                ax.plot(times, values, label=f"Flow {fid}", color=color, marker='o', linewidth=1)
            ax.set_title(title)
            ax.grid(True, linestyle="--", alpha=0.5)
            ax.legend()

        axs[-1].set_xlabel("Time (s)")
        plt.tight_layout(rect=[0, 0, 1, 0.97])
        plt.savefig(output_file, dpi=300)
        print(f"Saved all flow metric graphs to: {output_file}")

    def compare_multiple_traces(self,trace_files, labels=None, output_file="comparison_metrics.png"):
        self.parse()
        self.compute()
        self.print_summary()
        
        if labels is None:
            labels = [os.path.splitext(os.path.basename(f))[0] for f in trace_files]

        metrics = {
            "End-to-End Delay (s)": "delay_trace",
            "Inter-packet Delay (s)": "inter_arrival",
            "Throughput (kbps)": "throughput_trace",
            "Cumulative Received Packets": "recv_time_series"
        }

        num_metrics = len(metrics)
        num_traces = len(trace_files)
        fig, axs = plt.subplots(num_metrics, num_traces, figsize=(5 * num_traces, 3 * num_metrics), sharex='col')

        if num_traces == 1:
            axs = [[axs[i]] for i in range(num_metrics)]  # reshape to 2D

        for col, (tr_file, label) in enumerate(zip(trace_files, labels)):
            parser = Line_Plot(tr_file)
            parser.parse()
            parser.compute()

            flow_ids = list(parser.flow_data.keys())
            colors = list(cm.get_cmap("tab10").colors)

            for row, (metric_name, key) in enumerate(metrics.items()):
                ax = axs[row][col]
                for i, fid in enumerate(flow_ids):
                    data = parser.flow_data[fid]
                    series = sorted(data[key])
                    if not series:
                        continue
                    times = [pt[0] for pt in series]
                    values = [pt[1] for pt in series]
                    color = colors[i % len(colors)]
                    ax.plot(times, values, label=f"Flow {fid}", color=color, marker='o', linewidth=1)

                ax.set_title(f"{metric_name}\n({label})")
                ax.grid(True, linestyle='--', alpha=0.5)
                if row == num_metrics - 1:
                    ax.set_xlabel("Time (s)")
                if col == 0:
                    ax.set_ylabel(metric_name)

        handles, legend_labels = axs[0][0].get_legend_handles_labels()
        fig.legend(handles, legend_labels, loc='lower center', ncol=len(legend_labels), bbox_to_anchor=(0.5, -0.01))
        plt.tight_layout(rect=[0, 0.02, 1, 1])
        plt.savefig(output_file, dpi=300)
        print(f"Saved comparison plot to: {output_file}")
