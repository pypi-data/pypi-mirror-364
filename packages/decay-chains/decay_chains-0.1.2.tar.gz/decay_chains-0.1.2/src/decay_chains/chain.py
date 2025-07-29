import math
import matplotlib.pyplot as plt
import xml.etree.ElementTree as et
from importlib import resources

from decay_chains import Config


class DecayChain:
    sources = {}
    decay_info = {}
    atom_numbers = {}
    timesteps = []
    
    def __init__(self, config: Config):
        """
        Creates a DecayChain object, which handles the numerical integration of
        a decay chain.

        Parameters
        ----------
        config : decay_chains.Config
            A configuration object specifying nuclides and initial quantities.

        Returns
        -------
        decay_chains.DecayChain
            The DecayChain object initialized with the data from the
            configuration.
        """
        config.configure()
        self.sources = config.sources
        self.decay_info = config.decay_info
        self.atom_numbers = config.atom_numbers
            

    def decay_chain(self, timesteps: list | None = None):
        """
        Decays the chain of nuclides specified in input over each timestep in
        timesteps.

        Parameters
        ----------
        timesteps : list or None
            If None, the chain will be decayed for 1000 timesteps of a quarter
            of the half-life of the shortest-lived nuclide in the chain. If a
            list, each element specifies the length of an individual timestep
            in seconds (default is None).
        """
        if timesteps is None:
            half_lives = []
            for el in self.decay_info.keys():
                half_lives.append(self.decay_info[el]['half_life'])
            dt = min(half_lives) / 4
            timesteps = [dt] * 1000
        self.timesteps = timesteps
    
        # Decay each isotope
        time = 0
        for step in timesteps:
            time += step
            [self.atom_numbers[isotope].append(0) for isotope in self.atom_numbers.keys()]
            for isotope, n in self.atom_numbers.items():
                # Decay what exists: n[-1] becomes the current time
                n0 = n[-2] # The -1 element is the working element (currently 0)
                n1 = n0 * math.exp(-self.decay_info[isotope]['decay_const'] * step)
                self.atom_numbers[isotope][-1] += n1
        
                # Add the decay to the target if we care about it
                for target, ratio in self.decay_info[isotope]['targets'].items():
                    if target in self.atom_numbers.keys():
                        self.atom_numbers[target][-1] += (n0 - n1) * ratio
        
                # Add the source terms
                self.atom_numbers[isotope][-1] += step * self.sources[isotope]
                if self.atom_numbers[isotope][-1] < 0:
                    self.atom_numbers[isotope][-1] = 0
        

    def get_activity(self, nuclide: str) -> list[float]:
        """
        Returns a list of activities of a nuclide at each timestep.

        Parameters
        ----------
        nuclide : str
            The nuclide identifier. Ex. U238.
        
        Returns
        -------
        list of float
            A list containing the activities in Bq.
        """
        if nuclide not in self.atom_numbers.keys():
            return []
        l = self.decay_info[nuclide]['decay_const']
        return [l * n for n in self.atom_numbers[nuclide]]


    def get_atoms(self, nuclide: str) -> list[float]:
        """
        Returns a list of atom numbers of a nuclide at each timestep.

        Parameters
        ----------
        nuclide : str
            The nuclide identifier. Ex. U238.
        
        Returns
        -------
        list of float
            A list containing the atom numbers.
        """
        if nuclide not in self.atom_numbers.keys():
            return []
        return self.atom_numbers[nuclide]
        
        
    def plot_atoms(self):
        """
        Plots the number of atoms of all nuclides in the chain as a function of
        time.
        """
        # Create array of times from the timesteps for plotting
        xs = [0.]
        for step in self.timesteps:
            xs.append(xs[-1] + (step / (24 * 60 * 60)))
        # Plot the results
        print('Final number:')
        for isotope, ns in self.atom_numbers.items():
            plt.plot(xs, ns, label=isotope)
            print(f'\t{isotope}:\t{ns[-1]:6.4e} atoms')
        plt.title('Decay of Various Isotopes')
        plt.xlabel('Time [days]')
        plt.ylabel('Number []')
        plt.yscale('log')
        plt.legend()
        plt.show()
        

    def plot_activity(self):
        """
        Plots the activity of all nuclides in the chain as a function of time.
        """
        # Create array of times from the timesteps for plotting
        xs = [0.]
        for step in self.timesteps:
            xs.append(xs[-1] + (step / (24 * 60 * 60)))
        # Plot the results
        print('Final activity:')
        for isotope, ns in self.atom_numbers.items():
            decay_const = self.decay_info[isotope]['decay_const']
            a = [n * decay_const for n in ns]
            plt.plot(xs, a, label=isotope)
            print(f'\t{isotope}:\t{a[-1]:6.4e} Bq')
        plt.title('Decay of Various Isotopes')
        plt.xlabel('Time [days]')
        plt.ylabel('Activity [Bq]')
        plt.yscale('log')
        plt.legend()
        plt.show()
        

    def save_txt(self, output_file: str = "output.txt"):
        """
        Saves the output in a text file.

        Parameters
        ----------
        output_file : str
            The filename to write the output to (default is output.txt).
        """
        # Create array of times from the timesteps
        xs = [0.]
        for step in self.timesteps:
            xs.append(xs[-1] + (step / (24 * 60 * 60)))
        # Write the file
        with open(output_file, "w") as f:
            f.write('Time')
            for isotope in self.atom_numbers.keys():
                f.write(f'\t{isotope}')
            f.write('\n')
            values = list(self.atom_numbers.values())
            values = [list(tup) for tup in zip(*values)]
            for x, y in zip(xs, values):
                # if (x - math.floor(x)) < xs[1]:
                f.write(f'{x}')
                for val in y:
                    f.write(f'\t{val}')
                f.write('\n')
                
        
    @staticmethod
    def decay_photons(nuclide: str) -> tuple[list,list] | None:
        """
        Finds the decay photons for a given nuclide.
        
        Parameters
        ----------
        nuclide : str
            The nuclide identifier to look up. Ex. U238.

        Returns
        -------
        tuple[list[float], list[float]] or None
            A tuple with a list of photon energies and a list of corresponding
            photon intensities, or None if no decay photon data found.
        """
        chain_file = resources.path("decay_chains", "chain_endfb71_pwr.xml")
        with chain_file as f:
            chain = et.parse(f).getroot().findall('nuclide')
        for nuc in chain:
            info = nuc.attrib
            el = info['name']
            if el != nuclide:
                continue
            for source in nuc.findall('source'):
                s = source.attrib
                if s['particle'] != "photon":
                    continue
                dist = source.findall('parameters')[0].text
                if dist is None:
                    continue
                dist = [float(d) for d in dist.split()]
                idx = int(len(dist) / 2)
                energies = dist[:idx - 1]
                probs = dist[idx:]
                decay_const = math.log(2) / float(info['half_life'])
                probs = [p / decay_const for p in probs]
                return energies, probs
        return None


