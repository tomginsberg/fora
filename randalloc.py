import random
import numpy as np
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt


class RandomAllocator:
    def __init__(self, m, n):
        self.m = m
        self.n = n
        self.groups = ['O', 'A', 'B', 'AB']
        self.group_ids = list(range(len(self.groups)))
        self.patients = random.choices(self.group_ids, k=m)
        self.times = [1 for _ in self.patients]
        self.organs = random.choices(self.group_ids, k=n)

        self.tally = [[] for _ in self.groups]
        self.organs_allocated = 0
        self.allocation_times = [[] for _ in self.groups]

    def allocate(self):
        for i, o in enumerate(self.organs):
            utilities = [self.utility(p, o) for p in self.patients]
            matches = [i for i, u in enumerate(utilities) if u == 1]
            if len(matches) > 0:  # allocate the organ to a random patient
                match = random.choice(matches)
                p = self.patients.pop(match)
                wt = self.times.pop(match)
                self.tally[p].append(o)
                self.allocation_times[p].append(wt)
                self._increment_waiting_times()
                # mark the organ as allocated and remove it later to avoid iterating over mutating list
                self.organs[i] = None
                self.organs_allocated += 1
        self.organs = [o for o in self.organs if o is not None]

    def _increment_waiting_times(self):
        for i in range(len(self.times)):
            self.times[i] += 1

    def sample(self):
        self.patients += random.choices(self.group_ids, k=self.m)
        self.organs += random.choices(self.group_ids, k=self.n)
        self.times += [1 for _ in range(self.m)]

    @staticmethod
    def utility(patient, organ):
        if (patient == organ) or (organ == 0) or (patient == 3):
            return 1
        return 0

    def step(self, n=1):
        for i in tqdm(range(n)):
            self.allocate()
            self.sample()

    def print_tally(self):
        mean_wait_times = [np.mean(self.allocation_times[i]) for i in range(len(self.groups))]
        for i, g in enumerate(self.groups):
            cts = np.unique(self.tally[i], return_counts=True)
            tally = ' | '.join([f'{self.groups[idx]}: {c}' for idx, c in zip(*cts)])
            print(
                f'Patient Group: {g}\n'
                f'Organs Allocated: {tally}\n'
                f'Ratio of Total Organs Allocated: {len(self.tally[i]) / self.organs_allocated:.2f}\n'
                f'Average Time on Waitlist {mean_wait_times[i]:.2f}\n')

        print(f'Waiting Factor: {max(mean_wait_times) / min(mean_wait_times):.2f}')

    def waiting_histograms(self):
        for i in range(len(self.groups)):
            plt.hist(self.allocation_times[i], bins=20)
            plt.xlabel('Time on Waitlist')
            plt.title(f'Patient Group: {self.groups[i]}')
            plt.show()


if __name__ == '__main__':
    m = 10
    n = 10
    alloc = RandomAllocator(m, n)
    alloc.step(n=2000)
    alloc.print_tally()
    alloc.waiting_histograms()
