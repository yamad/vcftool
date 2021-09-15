import io

from vcftool.vcfparse import parse_header, variant_records


def test_parse_header():
    file = io.StringIO()
    file.write("##contig=<ID=1,length=1234>\n")
    file.seek(0)

    vcfmeta = parse_header(file)
    print(vcfmeta)
    assert vcfmeta.contigs["1"] == {"ID": "1", "length": "1234"}


def test_variant_record_single_allele():
    single_variant_vcf = "1	931393	.	G	T	2.17938e-13	.	AB=0;ABP=0;AC=0;AF=0;AN=6;AO=95;CIGAR=1X;DP=4124;DPB=4124;DPRA=0.999031;EPP=9.61615;EPPR=316.776;GTI=0;LEN=1;MEANALT=1;MQM=59.7579;MQMR=65.2274;NS=2;NUMALT=1;ODDS=591.29;PAIRED=0.989474;PAIREDR=0.966741;PAO=0;PQA=0;PQR=0;PRO=0;QA=3774;QR=160284;RO=4029;RPL=51;RPP=4.13032;RPPR=101.278;RPR=44;RUN=1;SAF=40;SAP=8.15326;SAR=55;SRF=1663;SRP=269.369;SRR=2366;TYPE=snp	GT:GQ:DP:DPR:RO:QR:AO:QA	0/0/0:132.995:2063:2063,0:2063:82063:0:0	0/0/0:132.995:2061:2061,95:1966:78221:95:3774"
    actual = list(variant_records(single_variant_vcf))
    assert [('1-931393-G-T', 'snp', '4124', 95, "2.36", '2.17938e-13')] == actual

def test_variant_record_multi_allele():
    multi_allele_vcf = "1	14108748	.	CAAAAAAAAAG	CAAAAAAAAG,CAAAAAAAAAAG	1.17455e-12	.	AB=0,0;ABP=0,0;AC=0,0;AF=0,0;AN=6;AO=106,52;CIGAR=1M1D9M,1M1I10M;DP=3964;DPB=4355.09;DPRA=0,0;EPP=32.5915,5.68288;EPPR=133.644;GTI=0;LEN=1,1;MEANALT=5,5;MQM=70,70;MQMR=70;NS=2;NUMALT=2;ODDS=1435.59;PAIRED=0.981132,0.923077;PAIREDR=0.979989;PAO=271.333,294.333;PQA=9028,9902;PQR=9902;PRO=294.333;QA=4164,1870;QR=147876;RO=3798;RPL=50,20;RPP=3.74778,9.02361;RPPR=3.03088;RPR=56,32;RUN=1,1;SAF=52,22;SAP=3.09224,5.68288;SAR=54,30;SRF=1646;SRP=149.397;SRR=2152;TYPE=del,ins	GT:GQ:DP:DPR:RO:QR:AO:QA	0/0/0:125.679:1982:1982,53,26:1899:73938:53,26:2082,935	0/0/0:125.679:1982:1982,53,26:1899:73938:53,26:2082,935"
    actual = list(variant_records(multi_allele_vcf))
    assert [("1-14108748-CAAAAAAAAAG-CAAAAAAAAG", "del", "3964", 106, "2.79", "1.17455e-12"),
            ("1-14108748-CAAAAAAAAAG-CAAAAAAAAAAG", "ins", "3964", 52, "1.37", "1.17455e-12"),
            ] == actual