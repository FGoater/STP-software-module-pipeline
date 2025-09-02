# STP-software-module-pipeline

<h3>Setup of the pipeline</h3>

Within the resources folder is a copy of the pipeline's input .json. Please input the file paths or DNAnexus file IDs of each input (apart from vep_version and vaf_threshold which should be numerical values) into the template. The filtering script can also be found in the resources folder of the repository and its file path should be inputted as the 'filtering_script' file in expanded_pipeline_input.json. 

<h3>Deployment in the cloud (DNAnexus)</h3>

Prior to initiating the pipeline, it is recommended to set up a resources or inputs folder containing your .fastqs, your genome reference files/indexes, your VEP tarball (https://grch37.ensembl.org/info/docs/tools/vep/script/vep_download.html) and the filtering script in the resource folder. 

Download the git repository with:
    git clone "https://github.com/FGoater/STP-software-module-pipeline/"

Navigate to the 'modules' folder and use DXcompile to create the pipeline applets in DNAnexus:
    java -jar /projects/dnanexus/dxCompiler-2.8.0.jar compile [workflow].wdl --destination project-[projectID]:[path-to-workflow-directory]

Collect and record the workflow ID when the pipeline has completed compiling.

Once 'expanded_pipeline_inputs.json' has been completed with DNAnexus file locations, transpile the .json:
    java -jar  /projects/dnanexus/dxCompiler-2.8.0.jar compile [path-to-expanded_pipeline_wf.wdl] -inputs expanded_pipeline_input.json --compileMode IR

Finally the pipeline can be run:
    dx run [workflow-ID] -f expanded_pipeline_input.dx.json --destination project-[ProjectID]:/file-path-to-DNAnexus-output-folder --delay-workspace-destruction

The pipeline can be monitored on the DNAnexus dashboard and dx download [fileID] can be used to pull down the outputs into your local workspace upon completion. 

<h2>Pipeline versions</h2>
<h4>Version 1.0.0 </h4>
Validated version of the pipeline with validation available. 
