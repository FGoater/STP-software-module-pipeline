version 1.0 # WDL version

task run_fastp {
    input {
        Array[File] fastq
        String out_name0 = sub(basename(fastq[0]),"\\.fastq", "")
        String out_name1 = sub(basename(fastq[1]),"\\.fastq", "")
    }

    command {
        fastp -i ~{fastq[0]} -I ~{fastq[1]} -o ~{out_name0}.fq.gz -O ~{out_name1}.fq.gz
    }

    output {
        File fastpreport = "fastp.html"
        Array[File] trimmedfastq = ["~{out_name0}.fq.gz","~{out_name1}.fq.gz"]
    }

    runtime {
        docker : "mattwherlock/fastp:0.23.2"
        memory : "8GB"
        cpu : 4
    }
}

