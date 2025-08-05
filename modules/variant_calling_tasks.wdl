version 1.0 # WDL version

task run_freebayes {
    input {
        File bamFile
        File baiFile
        File fa
        File fai
        File bed
        String out_name = sub(basename(bamFile),"\\.bam", "")
    }

    command {
        freebayes -f ~{fa} -t ~{bed} ~{bamFile} > ~{out_name}.vcf
    }

    output {
        File vcfFile = "~{out_name}.vcf"
    }

    runtime {
        docker : "swglh/freebayes:1.3.6"
        memory : "8GB"
        cpu : 4
    }
}
