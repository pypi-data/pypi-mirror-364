from functools import cached_property

from .blasting import (
    SpecializedBlastnSearch,
    formatted_blastn_search,
    BlastnSearch
)
from .convert import blast_format_bytes
from .sam import SAMBlastnSearch, merge_sam_bytes, sort_sam_bytes

class MultiformatBlastnSearch(SpecializedBlastnSearch):
    """A BlastnSearch using Blast4 archive (ASN.1) output for easy conversion.

    Although this class does not parse the output and, thus, provides no direct
    way of getting information out of the results, blast_formatter (and the
    functions in the simple_blast.convert module) can be used to quickly convert
    Blast4 archive format output to any other output format. Such conversions
    can be performed using the to* methods of this class. Hence, this class is
    useful when multiple representations of a given BLAST output are needed.

    Moreover, for some formats, such as SAM, additional information can be
    gleaned from the Blast4 archive format and used to correct problems with
    ncbi-blast+'s implementation of the output format.
    """
    out_formats = [11]

    @cached_property
    def output(self) -> bytes:
        """Get the cached blastn output as bytes."""
        return self.get_output()

    def to(self, out_format: int | str) -> bytes:
        """Convert the search output to another format.

        This function returns the raw bytes of the formatted output. If parsing
        is desired, see to_search and other to* methods.

        Parameters:
            out_format: The destination output format for conversion.

        Returns:
            The converted output, as bytes.
        """
        return blast_format_bytes(out_format, self.output)

    def to_search(self, out_format: int | str) -> BlastnSearch:
        """Convert the search, including output, to another format.

        Unlike to, this method produces a BlastnSearch object that retains the
        parameters used for this search. An appropriate subclass of BlastnSearch
        is chosen depending on the specified output format. For subclasses that
        cache and/or parse their results, the converted output will be used as
        the results for the new BlastnSearch instance, eliminating the need to
        re-run the search.

        For some output formats, such as SAM, simple_blast can perform
        corrections to the converted output using information from the
        MultiformatBlastnSearch (Blast4 archive, outfmt 11) output. This
        function will not perform such corrections automatically---specialized
        to* methods of this class should be used instead for that purpose.

        Parameters:
            out_format: The destination output format for conversion.

        Returns:
            The converted BlastnSearch.
        """
        return formatted_blastn_search(out_format)._load_results(
            self.to(out_format),
            subject = self.subject,
            query = self.query,
            out_format = out_format,
            evalue = self.evalue,
            db_cache = self.db_cache,
            threads = self.threads,
            dust = self.dust,
            task = self.task,
            max_targets = self.max_targets,
            n_seqidlist = self.negative_seqidlist,
            perc_ident = self.perc_identity,
            debug = self.debug
        )

    def to_sam(
            self,
            decode: bool = True,
            subject_as_reference: bool = False,
            sort: bool = True,
    ) -> SAMBlastnSearch:
        """Convert this search to SAM format.

        By default, ncbi-blast+ uses its "internal" subject and query names
        (e.g., "Query_1", or "Subject_1") in the SAM output. Unlike the generic
        to_search method, this method can correct those names in the converted
        search output.

        Parameters:
            decode (bool):               Correct the subject/query names.
            subject_as_reference (bool): Use subject sequences as references.
            sort (bool):                 Sort the SAM output using samtools.

        Returns:
            A SAMBlastnSearch converted from this search.
        """
        import pyblast4_archive
        b4s = pyblast4_archive.Blast4Archive.from_bytes(
            self.output,
            "asn_text"
        )
        out_format = SAMBlastnSearch.out_formats[0]
        if subject_as_reference:
            out_format = f"{out_format} SR"
        sams = [
            blast_format_bytes(out_format, str(b4).encode("utf-8"))
            for b4 in b4s
        ]
        sams = [s for s in sams if s]
        #
        res = merge_sam_bytes(*sams)
        if sort:
            res = sort_sam_bytes(res)
        decode_query = {}
        decode_subject = {}
        if decode:
            decode_query = pyblast4_archive.decode_query_ids(b4s)
            decode_subject = pyblast4_archive.decode_subject_ids(b4s)
            if (db_path := self.get_db()) is not None and not self.remote:
                #from IPython import embed; embed()
                db = pyblast4_archive.SeqDB(db_path, "nucleotide")
                decode_subject |= {
                    f"BL_ORD_ID:{k}": v
                    for (k, v)
                    in pyblast4_archive.decode_database_oids(b4s, db).items()
                }
            if subject_as_reference:
                tmp = decode_subject
                decode_subject = decode_query
                decode_query = tmp
        #from IPython import embed; embed()
        # noinspection PyProtectedMember
        sam = SAMBlastnSearch._load_results(
            res,
            subject = self.subject,
            query = self.query,
            evalue = self.evalue,
            db_cache = self.db_cache,
            threads = self.threads,
            dust = self.dust,
            task = self.task,
            max_targets = self.max_targets,
            n_seqidlist = self.negative_seqidlist,
            perc_ident = self.perc_identity,
            debug = self.debug,
            decode_target = decode_query,
            decode_query = decode_subject
        )
        sam._output = res
        #from IPython import embed; embed()
        return sam

    @classmethod
    def _load_results(cls, res, **kwargs):
        try:
            assert int(kwargs["out_format"]) in cls.out_formats
            del kwargs["out_format"]
        except KeyError:
            pass
        search = cls(**kwargs)
        return search
        

