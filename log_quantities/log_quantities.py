import hoomd
from hoomd import md
import numpy
hoomd.context.initialize()

system = hoomd.init.read_gsd(filename='init.gsd')

# force field setup
harmonic = md.bond.harmonic()
harmonic.bond_coeff.set('polymer', k=330.0, r0=0.84)
nl = md.nlist.cell()
lj = md.pair.lj(nlist = nl, r_cut=3.0)
lj.pair_coeff.set('A', 'A', epsilon=1.0, sigma=1.0, alpha=0.0)
lj.pair_coeff.set('A', 'B', epsilon=1.0, sigma=1.0, alpha=0.0)
lj.pair_coeff.set('B', 'B', epsilon=1.0, sigma=1.0, alpha=1.0)

# NVT integration
all = hoomd.group.all()
md.integrate.mode_standard(dt=0.005)
md.integrate.nvt(group=all, kT=1.2, tau=0.5)

nl.set_params(r_buff=0.4, check_period=5)

log = hoomd.analyze.log(quantities=['potential_energy'], filename=None, period=None)

gsd = hoomd.dump.gsd(filename="trajectory.gsd", period=1000, group=hoomd.group.all(), overwrite=True)
gsd.log['particles/potential_energy'] = lambda step: numpy.array([p.net_energy for p in system.particles], dtype=numpy.float32)
gsd.log['particles/net_force'] = lambda step: numpy.array([p.net_force for p in system.particles], dtype=numpy.float32)
gsd.log['potential_energy'] = lambda step: numpy.array([log.query('potential_energy')], dtype=numpy.float64)
message = 'hello OVITO'
gsd.log['string'] = lambda step: numpy.array([message], dtype=numpy.dtype((bytes, len(message)+1))).view(dtype=numpy.int8)
gsd.log['bonds/tag'] = lambda step: numpy.array([b.tag for b in system.bonds], dtype=numpy.uint32)

hoomd.run(1)
del gsd.log['bonds/tag']
del gsd.log['string']

# Run for 10,000 time steps
hoomd.run(10e3)


