version 1.0 # WDL version


task run_bwamem2 {
    input {
        Array [File] fastq
        File fa
        File amb
        File ann
        File b2bit
        File a0123
        File fai
        File pac
        String out_name = sub(basename(fastq[1]),"\\.fastq", "")
    }

    command <<<
        bwa-mem2 mem ~{fa} ~{sep= " " fastq}> ~{out_name}_alignment.sam    >>>

    output {
        File samFile = "~{out_name}_alignment.sam"
    }

    runtime {
        docker : "swglh/bwamem2:v2.2.1"
        memory : "80 GB"
        cpu : 24
    }
}