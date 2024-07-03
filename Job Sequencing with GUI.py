import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
import numpy as np

class WelcomeGui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("JobScheduler")
        self.geometry("500x300")

        label1 = tk.Label(self, text="JobScheduler", font=("Book Antiqua", 50))
        label1.place(x=50, y=50, width=400, height=100)

        button1 = tk.Button(self, text="Get Started", background="#c3ced2", command=self.start_mpr_gui)
        button1.place(x=150, y=200, width=200, height=50)

    def start_mpr_gui(self):
        self.destroy()
        MPRGUI()

class MPRGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.nom_var = tk.StringVar()
        self.noj_var = tk.StringVar()
        self.pt_var = tk.StringVar()

        self.title("MPR Calculator")
        self.geometry("600x400")

        # Labels and Entries
                
        nom_label = tk.Label(self, text="Enter the number of machines:")
        nom_label.grid(row=0, column=0, sticky="w")
        self.nom_entry = tk.Entry(self, textvariable=self.nom_var)
        self.nom_entry.grid(row=0, column=1, sticky="w")

        noj_label = tk.Label(self, text="Enter the number of jobs:")
        noj_label.grid(row=1, column=0, sticky="w")
        self.noj_entry = tk.Entry(self, textvariable=self.noj_var)
        self.noj_entry.grid(row=1, column=1, sticky="w")

        pt_label = tk.Label(self, text="Enter the processing times (J1M1, J1M2, J1M3...):")
        pt_label.grid(row=2, column=0, sticky="w")
        self.pt_text = tk.Text(self, height=5, width=20)
        self.pt_text.grid(row=2, column=1, sticky="w")

        # Calculate Button
        calculate_button = tk.Button(self, text="Calculate", command=self.calculate_mpr)
        calculate_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Result Text
        self.result_text = tk.Text(self, height=10, width=50)
        self.result_text.grid(row=4, column=0, columnspan=2)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.destroy()

    def calculate_mpr(self):
        nom = int(self.nom_var.get())
        noj = int(self.noj_var.get())

        PT = [[0] * nom for _ in range(noj)]

        for i in range(noj):
            for j in range(nom):
                PT[i][j] = int(self.pt_text.get("1.0", tk.END).split()[i * nom + j])

        mptFM = float('inf')
        mptLM = float('inf')

        for i in range(noj):
            ptFM = PT[i][0]
            ptLM = PT[i][nom - 1]
            mptFM = min(mptFM, ptFM)
            mptLM = min(mptLM, ptLM)

        maxPT = [max(PT[i][1:nom - 1]) for i in range(noj)]
        maxmaxPT = max(maxPT)

        if mptFM < maxmaxPT and mptLM < maxmaxPT:
            result_text = "Cannot continue with this method. Change the inputs."
            messagebox.showinfo("Result", result_text)
            return

        machineG = [sum(PT[i][:-1]) for i in range(noj)]
        machineI = [sum(PT[i][1:]) for i in range(noj)]

        allocated = [False] * noj
        OS = [0] * noj
        count = 0

        for slot in range(noj):
            mdI = float('inf')
            mdG = float('inf')
            iJI = -1
            gJI = -1

            for i in range(noj):
                if not allocated[i] and machineG[i] < mdG:
                    mdG = machineG[i]
                    gJI = i

            for i in range(noj):
                if not allocated[i] and machineI[i] < mdI:
                    mdI = machineI[i]
                    iJI = i

            if mdG <= mdI:
                OS[count] = gJI + 1
                allocated[gJI] = True
                count += 1

            if mdI < mdG:
                OS[noj - slot - 1] = iJI + 1
                allocated[iJI] = True

        outTimes = [[0] * noj for _ in range(nom)]

        for i in range(noj):
            job = OS[i] - 1
            for j in range(nom):
                if i == 0:
                    if j == 0:
                        outTimes[j][i] = PT[job][j]
                    else:
                        outTimes[j][i] = outTimes[j - 1][i] + PT[job][j]
                else:
                    if j == 0:
                        outTimes[j][i] = outTimes[j][i - 1] + PT[job][j]
                    else:
                        outTimes[j][i] = max(outTimes[j - 1][i], outTimes[j][i - 1]) + PT[job][j]

        inTimes = [[outTimes[j][i] - PT[OS[i] - 1][j] for i in range(noj)] for j in range(nom)]

        minElapsed = outTimes[nom - 1][noj - 1]
        idleTimes = [0] * nom

        for i in range(nom):
            lastOutTime = outTimes[i][noj - 1]
            firstInTime = inTimes[i][0]
            idleTimes[i] = (minElapsed - lastOutTime) + firstInTime

            for j in range(1, noj):
                inTime = inTimes[i][j]
                outTime = outTimes[i][j - 1]
                idle = inTime - outTime

                if idle > 0:
                    idleTimes[i] += idle

        result = "\nOptimal Sequence: "
        for i in range(noj):
            result += str(OS[i]) + "  "
        result += "\n\nMinimum Elapsed Time: " + str(minElapsed)
        result += "\n\nIdle Time for Each Machine:\n"
        for i in range(nom):
            result += f"Machine {i + 1}: {idleTimes[i]}\n"

        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, result)

        # Gantt Chart
        

        # Plotting Gantt chart for each machine
        for machine_index in range(len(inTimes)):
            jobs_schedule = [(i, inTimes[machine_index][i], outTimes[machine_index][i])
                             for i in range(len(inTimes[machine_index]))]
            machine_idle_times = [(outTimes[machine_index][i], inTimes[machine_index][i+1])
                                  for i in range(len(inTimes[machine_index])-1)]
            machine_idle_times.append((outTimes[machine_index][-1], minElapsed))
            self.plot_gantt_chart(machine_index, jobs_schedule, machine_idle_times)


    def plot_gantt_chart(self, machine_index, jobs_schedule, machine_idle_times):
        fig = plt.figure(figsize=(10, 3))
        ax = fig.add_subplot(111)

        y_labels = [f"Machine {machine_index + 1}"]
        ax.set_yticks([1])
        ax.set_yticklabels(y_labels)

        tasks = []
        colors = []

        # Assigning colors to jobs
        job_colors = plt.cm.tab20.colors  
        job_color_index = 0

        for start, end in machine_idle_times:
            tasks.append(("Idle", start, end))
            colors.append('#edebe4')  

        for job_index, start_time, end_time in jobs_schedule:
            tasks.append((f"Job {job_index + 1}", start_time, end_time))

            # Assigning a different color to each job
            colors.append(job_colors[job_color_index])
            job_color_index = (job_color_index + 1) % len(job_colors)

        for i, task in enumerate(tasks):
            task_name, start, end = task
            ax.barh(y=1, width=end-start, left=start, height=0.3, color=colors[i], align='center')
            ax.text((start+end)/2, 1, task_name, ha='center', va='center', color='black', fontsize=8)

        ax.set_xlabel('Time')
        ax.set_title(f'Gantt Chart for Machine {machine_index + 1}')

        # Adjusting x-axis ticks for better readability
        max_end_time = max(end for _, _, end in tasks)
        ax.set_xticks(np.arange(0, max_end_time + 6, 5))

        plt.grid(True)
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    WelcomeGui().mainloop()

# 14 10 4 6 18 12 12 8 10 20 10 8 10 12 16 16 6 6 4 12

