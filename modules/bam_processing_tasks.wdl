version 1.0 # WDL version


task run_samstoolsconvert {
    input {
        File samFile
        String out_name = sub(basename(samFile),"\\.sam", "")
    }

    command {
        samtools view -S -b ~{samFile} > ~{out_name}.bam
    }

    output {
        File bamFile = "~{out_name}.bam"
    }

    runtime {
        docker : "swglh/samtools:1.18"
        memory : "8GB"
        cpu : 4
    }
}

task run_samstoolssort {
    input {
        File bamFile
        String out_name = sub(basename(bamFile),"\\.bam", "")
    }

    command {
        samtools sort ~{bamFile} -o ~{out_name}sorted.bam &&
        samtools index -b ~{out_name}sorted.bam 
    }

    output {
        File bamFileSorted = "~{out_name}sorted.bam"
        File baiFile = "~{out_name}sorted.bam.bai"
        
    }

    runtime {
        docker : "swglh/samtools:1.18"
        memory : "8GB"
        cpu : 4
    }
}

task run_samstoolsindex {
    input {
        File bamFileSorted
        String out_name = sub(basename(bamFileSorted),"\\.bam", "")
    }

    command {
        samtools index -b ~{bamFileSorted} &&
        cp /inputs/~{out_name}.bam.bai /execution/
    }

    output {
        File baiFile = "~{out_name}.bam.bai"
    }

    runtime {
        docker : "swglh/samtools:1.18"
        memory : "8GB"
        cpu : 4
    }
}
