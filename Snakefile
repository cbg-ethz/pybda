configfile: "config.yaml"

rule all:
    input:
    	expand("{sample}/dimension-reduction", sample=config["outfolder"]),
      	expand("{sample}/outlier-removal", sample=config["outfolder"])

rule dimred:
    input:
        expand("{sample}", sample=config["samples"])
    output:
        expand("{sample}/dimension-reduction", sample=config["outfolder"])
    shell:
        "cat {input} > {output}"

rule outliers:
    input:
        expand("{sample}/dimension-reduction", sample=config["outfolder"]),
    output:
        expand("{sample}/outlier-removal", sample=config["outfolder"])
    shell:
        "cat {input} > {output}"
