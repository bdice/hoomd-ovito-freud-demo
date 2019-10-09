from flow import FlowProject
import garnett


class Project(FlowProject):
    pass


@Project.label
def completed(job):
    return job.isfile('dump.gsd') or job.doc.get('failed', False)


@Project.operation
@Project.pre.isfile('dump.pos')
@Project.post(completed)
def make_gsd(job):
    try:
        with garnett.read(job.fn('dump.pos')) as traj:
            garnett.write(traj, job.fn('dump.gsd'))
    except garnett.errors.ParserError as e:
        print(e)
        job.doc.failed = True


if __name__ == '__main__':
    Project().main()
