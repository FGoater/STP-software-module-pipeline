version 1.0 #WDL version

task run_filter_script {
    input {
        File? filtering_script
        File annotated_vcf
        String vaf_threshold
        String out_name = sub(basename(annotated_vcf),"\\.vcf", "")
    }

    command {
        python3 ~{filtering_script} ~{annotated_vcf} ${out_name}_filtered.vcf ${vaf_threshold} ${out_name}_filtering_log.log
    }

    output {
        File? filtered_vcf_output = "${out_name}_filtered.vcf"
        File? filter_logs = "${out_name}_filtering_log.log"
    }

    runtime {
        docker : "ffgoater/vcffilter:1"
        memory : "16GB"
        cpu : 8
    }
}

