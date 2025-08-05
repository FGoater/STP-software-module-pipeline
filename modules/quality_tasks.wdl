version 1.0 # WDL version

task run_fastqc {
    input {
        File fastq
        String out_name = sub(basename(fastq),"\\.fastq", "") #sets the  name of the fastqc based on the name of the fastq file
    }

    command <<<
        fastqc -o . ~{fastq} > ~{out_name}_fastqc.html
    >>>

    output {
        File fastqc_report = "~{out_name}_fastqc.html"
    }

    runtime {
        docker : "swglh/fastqc:v0.11.9"
        memory : "16GB"
        cpu : 8
        continueOnReturnCode: true
    }
}
