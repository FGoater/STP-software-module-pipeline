version 1.0 # WDL version

task run_vep {
    input {
        File vcfFile
        File fa
        File vep_tarball
        String vep_version
        String out_name = sub(basename(vcfFile),"\\.vcf", "")
    }

    command {
        cp ~{vep_tarball} .
        tar --no-same-owner -xzf ~{basename(vep_tarball)}
        chmod -R a+rX .

        vep  -i ~{vcfFile} -o ~{out_name}_annotated.vcf --vcf --cache_version ~{vep_version} --no_stats --cache --dir_cache . --offline --merged --skipped_variants_file ~{out_name}.skipped.txt --fork 16 --fasta ~{fa} --assembly GRCh38 --everything --hgvsg --show_ref_allele --uploaded_allele --check_existing --transcript_version

    }

    output {
        File annotatedVariantsFile = "~{out_name}_annotated.vcf"
        File skippedvariantsfile = "~{out_name}.skipped.txt"
    }

    runtime {
        docker: "swglh/ensembl-vep:86"
        memory: "12G"
        cpu: 12
    }
}




