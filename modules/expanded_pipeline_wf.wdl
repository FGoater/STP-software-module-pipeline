version 1.0

import "quality_tasks.wdl" as quality_tasks
import "trimming_tasks.wdl" as trimming_tasks
import "alignment_tasks.wdl" as alignment_tasks
import "bam_processing_tasks.wdl" as bam_processing_tasks
import "variant_calling_tasks.wdl" as variant_calling_tasks
import "variant_annotation_tasks.wdl" as variant_annotation_tasks
import "filtering_task.wdl" as filtering_task

workflow expanded_pipeline_inputs {
    meta {
        developer: "SWGLH-FG"
        date: "05.08.2025"
        version: "1.0.0"
    }
    input {
        Array[Array[File]] fastqs
        File fa
        File amb
        File ann
        File b2bit
        File a0123
        File fai
        File pac
        File bed
        File vep_tarball
        String vep_version
        File? filtering_script
        String vaf_threshold
    }

    scatter (i in range(length(fastqs))) {
        call trimming_tasks.run_fastp {
            input:
                fastq = fastqs[i]
        }

        scatter (f in fastqs[i]) {
            call quality_tasks.run_fastqc {
                input: 
                    fastq = f
            }
        }

        call alignment_tasks.run_bwamem2 {
            input:
                fastq = run_fastp.trimmedfastq,
                fa = fa,
                amb = amb,
                ann = ann,
                b2bit = b2bit,
                a0123 = a0123,
                fai = fai,
                pac = pac
        }

        call bam_processing_tasks.run_samstoolsconvert {
            input:
                samFile = run_bwamem2.samFile
        }

        call bam_processing_tasks.run_samstoolssort {
            input:
                bamFile = run_samstoolsconvert.bamFile
        }

        call variant_calling_tasks.run_freebayes {
            input:
                bamFile = run_samstoolssort.bamFileSorted,
                fa = fa,
                bed = bed, 
                baiFile = run_samstoolssort.baiFile,
                fai = fai
        }

        call variant_annotation_tasks.run_vep {
            input:
                vcfFile = run_freebayes.vcfFile,
                vep_tarball = vep_tarball,
                vep_version = vep_version,
                fa = fa
        }

        call filtering_task.run_filter_script {
            input:
                annotated_vcf = run_vep.annotatedVariantsFile,
                vaf_threshold = vaf_threshold,
                filtering_script = filtering_script
        }
    }

    output {
        Array[Array[File]] fastqReports = run_fastqc.fastqc_report
        Array[Array[File]] fastqtrim = run_fastp.trimmedfastq
        Array[File] fastpreports = run_fastp.fastpreport
        Array[File] samFiles = run_bwamem2.samFile
        Array[File] bamFiles = run_samstoolsconvert.bamFile
        Array[File] bamFilesSorted = run_samstoolssort.bamFileSorted
        Array[File] baiFiles = run_samstoolssort.baiFile
        Array[File] vcfFiles = run_freebayes.vcfFile
        Array[File] annotatedVarFiles = run_vep.annotatedVariantsFile
        Array[File?] skippedvarfiles = run_vep.skippedvariantsfile
        Array[File?] filtered_vcfs = run_filter_script.filtered_vcf_output
        Array[File?] filtering_logs = run_filter_script.filter_logs 
    }
}
