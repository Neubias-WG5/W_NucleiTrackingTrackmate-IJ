import sys
from cytomine.models import Job
from subprocess import call
from neubiaswg5 import CLASS_PRTTRK
from neubiaswg5.helpers import NeubiasJob, prepare_data, upload_data, upload_metrics

def main(argv):
    with NeubiasJob.from_cli(argv) as nj:
        problem_cls = CLASS_PRTTRK
        is_2d = False

        nj.job.update(status=Job.RUNNING, progress=0, statusComment="Initialisation...")
        in_images, gt_images, in_path, gt_path, out_path, tmp_path = prepare_data(problem_cls, nj, is_2d=is_2d, **nj.flags)

        # 2. Call the image analysis workflow
        nj.job.update(progress=25, statusComment="Launching workflow...")
        command = "/usr/bin/xvfb-run ./ImageJ-linux64 --ij2 --headless --console --run " \
		   "/fiji/macros/Trackmate_script.py input={},output={},rad={},thr={},dst={},gapdst={},gap={},minlgth={}" \
		   .format(in_path, out_path, nj.parameters.rad, nj.parameters.thr, nj.parameters.dst, nj.parameters.gapdst, nj.parameters.gap, nj.parameters.minlgth)	
        return_code = call(command, shell=True, cwd="/fiji")  # waits for the subprocess to return

        if return_code != 0:
            err_desc = "Failed to execute the ImageJ script (return code: {})".format(return_code)
            nj.job.update(progress=100, statusComment=err_desc)
            raise ValueError(err_desc)

        # 4. Create and upload annotations
        nj.job.update(progress=70, statusComment="Uploading extracted annotation...")
        upload_data(problem_cls, nj, in_images, out_path, **nj.flags, is_2d=is_2d, monitor_params={
            "start": 70, "end": 90, "period": 0.1
        })

        # 5. Compute and upload the metrics       
        nj.job.update(progress=90, statusComment="Computing and uploading metrics (if necessary)...")
        upload_metrics(problem_cls, nj, in_images, gt_path, out_path, tmp_path, **nj.flags)

        # 6. End the job
        nj.job.update(status=Job.TERMINATED, progress=100, statusComment="Finished.")


if __name__ == "__main__":
    main(sys.argv[1:])

