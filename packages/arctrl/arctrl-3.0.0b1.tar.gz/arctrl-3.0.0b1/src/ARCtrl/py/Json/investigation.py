from __future__ import annotations
from collections.abc import Callable
from typing import (Any, TypeVar)
from ..fable_modules.fable_library.date import (today, to_string)
from ..fable_modules.fable_library.list import (choose, of_array, FSharpList, unzip, empty)
from ..fable_modules.fable_library.option import (map, default_arg)
from ..fable_modules.fable_library.seq import (map as map_1, concat)
from ..fable_modules.fable_library.seq2 import distinct_by
from ..fable_modules.fable_library.types import Array
from ..fable_modules.fable_library.util import (IEnumerable_1, string_hash)
from ..fable_modules.thoth_json_core.decode import (object, IRequiredGetter, string, IOptionalGetter, resize_array, IGetters, list_1 as list_1_1)
from ..fable_modules.thoth_json_core.types import (IEncodable, IEncoderHelpers_1, Decoder_1)
from ..Core.arc_types import (ArcAssay, ArcStudy, ArcInvestigation)
from ..Core.comment import Comment
from ..Core.Helper.identifier import create_missing_identifier
from ..Core.ontology_annotation import OntologyAnnotation
from ..Core.ontology_source_reference import OntologySourceReference
from ..Core.person import Person
from ..Core.publication import Publication
from ..Core.Table.composite_cell import CompositeCell
from .assay import (encoder as encoder_4, decoder as decoder_6, encoder_compressed as encoder_compressed_1, decoder_compressed as decoder_compressed_1)
from .comment import (encoder as encoder_6, decoder as decoder_8, ROCrate_encoder as ROCrate_encoder_5, ROCrate_decoder as ROCrate_decoder_5, ISAJson_encoder as ISAJson_encoder_5, ISAJson_decoder as ISAJson_decoder_5)
from .context.rocrate.isa_investigation_context import context_jsonvalue
from .context.rocrate.rocrate_context import (conforms_to_jsonvalue, context_jsonvalue as context_jsonvalue_1)
from .decode import Decode_objectNoAdditionalProperties
from .encode import (try_include, try_include_seq)
from .ontology_source_reference import (encoder as encoder_1, decoder as decoder_3, ROCrate_encoder as ROCrate_encoder_1, ROCrate_decoder as ROCrate_decoder_2, ISAJson_encoder as ISAJson_encoder_1, ISAJson_decoder as ISAJson_decoder_2)
from .person import (encoder as encoder_3, decoder as decoder_5, ROCrate_encoder as ROCrate_encoder_3, ROCrate_decoder as ROCrate_decoder_4, ISAJson_encoder as ISAJson_encoder_3, ISAJson_decoder as ISAJson_decoder_4)
from .publication import (encoder as encoder_2, decoder as decoder_4, ROCrate_encoder as ROCrate_encoder_2, ROCrate_decoder as ROCrate_decoder_3, ISAJson_encoder as ISAJson_encoder_2, ISAJson_decoder as ISAJson_decoder_3)
from .study import (encoder as encoder_5, decoder as decoder_7, encoder_compressed as encoder_compressed_2, decoder_compressed as decoder_compressed_2, ROCrate_encoder as ROCrate_encoder_4, ROCrate_decoder as ROCrate_decoder_1, ISAJson_encoder as ISAJson_encoder_4, ISAJson_decoder as ISAJson_decoder_1)

__A_ = TypeVar("__A_")

def encoder(inv: ArcInvestigation) -> IEncodable:
    def chooser(tupled_arg: tuple[str, IEncodable | None], inv: Any=inv) -> tuple[str, IEncodable] | None:
        def mapping(v_1: IEncodable, tupled_arg: Any=tupled_arg) -> tuple[str, IEncodable]:
            return (tupled_arg[0], v_1)

        return map(mapping, tupled_arg[1])

    def _arrow3196(__unit: None=None, inv: Any=inv) -> IEncodable:
        value: str = inv.Identifier
        class ObjectExpr3195(IEncodable):
            def Encode(self, helpers: IEncoderHelpers_1[Any]) -> Any:
                return helpers.encode_string(value)

        return ObjectExpr3195()

    def _arrow3198(value_1: str, inv: Any=inv) -> IEncodable:
        class ObjectExpr3197(IEncodable):
            def Encode(self, helpers_1: IEncoderHelpers_1[Any]) -> Any:
                return helpers_1.encode_string(value_1)

        return ObjectExpr3197()

    def _arrow3200(value_3: str, inv: Any=inv) -> IEncodable:
        class ObjectExpr3199(IEncodable):
            def Encode(self, helpers_2: IEncoderHelpers_1[Any]) -> Any:
                return helpers_2.encode_string(value_3)

        return ObjectExpr3199()

    def _arrow3202(value_5: str, inv: Any=inv) -> IEncodable:
        class ObjectExpr3201(IEncodable):
            def Encode(self, helpers_3: IEncoderHelpers_1[Any]) -> Any:
                return helpers_3.encode_string(value_5)

        return ObjectExpr3201()

    def _arrow3204(value_7: str, inv: Any=inv) -> IEncodable:
        class ObjectExpr3203(IEncodable):
            def Encode(self, helpers_4: IEncoderHelpers_1[Any]) -> Any:
                return helpers_4.encode_string(value_7)

        return ObjectExpr3203()

    def _arrow3205(osr: OntologySourceReference, inv: Any=inv) -> IEncodable:
        return encoder_1(osr)

    def _arrow3206(oa: Publication, inv: Any=inv) -> IEncodable:
        return encoder_2(oa)

    def _arrow3207(person: Person, inv: Any=inv) -> IEncodable:
        return encoder_3(person)

    def _arrow3208(assay: ArcAssay, inv: Any=inv) -> IEncodable:
        return encoder_4(assay)

    def _arrow3209(study: ArcStudy, inv: Any=inv) -> IEncodable:
        return encoder_5(study)

    def _arrow3211(value_9: str, inv: Any=inv) -> IEncodable:
        class ObjectExpr3210(IEncodable):
            def Encode(self, helpers_5: IEncoderHelpers_1[Any]) -> Any:
                return helpers_5.encode_string(value_9)

        return ObjectExpr3210()

    def _arrow3212(comment: Comment, inv: Any=inv) -> IEncodable:
        return encoder_6(comment)

    values: FSharpList[tuple[str, IEncodable]] = choose(chooser, of_array([("Identifier", _arrow3196()), try_include("Title", _arrow3198, inv.Title), try_include("Description", _arrow3200, inv.Description), try_include("SubmissionDate", _arrow3202, inv.SubmissionDate), try_include("PublicReleaseDate", _arrow3204, inv.PublicReleaseDate), try_include_seq("OntologySourceReferences", _arrow3205, inv.OntologySourceReferences), try_include_seq("Publications", _arrow3206, inv.Publications), try_include_seq("Contacts", _arrow3207, inv.Contacts), try_include_seq("Assays", _arrow3208, inv.Assays), try_include_seq("Studies", _arrow3209, inv.Studies), try_include_seq("RegisteredStudyIdentifiers", _arrow3211, inv.RegisteredStudyIdentifiers), try_include_seq("Comments", _arrow3212, inv.Comments)]))
    class ObjectExpr3213(IEncodable):
        def Encode(self, helpers_6: IEncoderHelpers_1[Any], inv: Any=inv) -> Any:
            def mapping_1(tupled_arg_1: tuple[str, IEncodable]) -> tuple[str, __A_]:
                return (tupled_arg_1[0], tupled_arg_1[1].Encode(helpers_6))

            arg: IEnumerable_1[tuple[str, __A_]] = map_1(mapping_1, values)
            return helpers_6.encode_object(arg)

    return ObjectExpr3213()


def _arrow3226(get: IGetters) -> ArcInvestigation:
    def _arrow3214(__unit: None=None) -> str:
        object_arg: IRequiredGetter = get.Required
        return object_arg.Field("Identifier", string)

    def _arrow3215(__unit: None=None) -> str | None:
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("Title", string)

    def _arrow3216(__unit: None=None) -> str | None:
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("Description", string)

    def _arrow3217(__unit: None=None) -> str | None:
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("SubmissionDate", string)

    def _arrow3218(__unit: None=None) -> str | None:
        object_arg_4: IOptionalGetter = get.Optional
        return object_arg_4.Field("PublicReleaseDate", string)

    def _arrow3219(__unit: None=None) -> Array[OntologySourceReference] | None:
        arg_11: Decoder_1[Array[OntologySourceReference]] = resize_array(decoder_3)
        object_arg_5: IOptionalGetter = get.Optional
        return object_arg_5.Field("OntologySourceReferences", arg_11)

    def _arrow3220(__unit: None=None) -> Array[Publication] | None:
        arg_13: Decoder_1[Array[Publication]] = resize_array(decoder_4)
        object_arg_6: IOptionalGetter = get.Optional
        return object_arg_6.Field("Publications", arg_13)

    def _arrow3221(__unit: None=None) -> Array[Person] | None:
        arg_15: Decoder_1[Array[Person]] = resize_array(decoder_5)
        object_arg_7: IOptionalGetter = get.Optional
        return object_arg_7.Field("Contacts", arg_15)

    def _arrow3222(__unit: None=None) -> Array[ArcAssay] | None:
        arg_17: Decoder_1[Array[ArcAssay]] = resize_array(decoder_6)
        object_arg_8: IOptionalGetter = get.Optional
        return object_arg_8.Field("Assays", arg_17)

    def _arrow3223(__unit: None=None) -> Array[ArcStudy] | None:
        arg_19: Decoder_1[Array[ArcStudy]] = resize_array(decoder_7)
        object_arg_9: IOptionalGetter = get.Optional
        return object_arg_9.Field("Studies", arg_19)

    def _arrow3224(__unit: None=None) -> Array[str] | None:
        arg_21: Decoder_1[Array[str]] = resize_array(string)
        object_arg_10: IOptionalGetter = get.Optional
        return object_arg_10.Field("RegisteredStudyIdentifiers", arg_21)

    def _arrow3225(__unit: None=None) -> Array[Comment] | None:
        arg_23: Decoder_1[Array[Comment]] = resize_array(decoder_8)
        object_arg_11: IOptionalGetter = get.Optional
        return object_arg_11.Field("Comments", arg_23)

    return ArcInvestigation(_arrow3214(), _arrow3215(), _arrow3216(), _arrow3217(), _arrow3218(), _arrow3219(), _arrow3220(), _arrow3221(), _arrow3222(), _arrow3223(), None, None, _arrow3224(), _arrow3225())


decoder: Decoder_1[ArcInvestigation] = object(_arrow3226)

def encoder_compressed(string_table: Any, oa_table: Any, cell_table: Any, inv: ArcInvestigation) -> IEncodable:
    def chooser(tupled_arg: tuple[str, IEncodable | None], string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, inv: Any=inv) -> tuple[str, IEncodable] | None:
        def mapping(v_1: IEncodable, tupled_arg: Any=tupled_arg) -> tuple[str, IEncodable]:
            return (tupled_arg[0], v_1)

        return map(mapping, tupled_arg[1])

    def _arrow3230(__unit: None=None, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, inv: Any=inv) -> IEncodable:
        value: str = inv.Identifier
        class ObjectExpr3229(IEncodable):
            def Encode(self, helpers: IEncoderHelpers_1[Any]) -> Any:
                return helpers.encode_string(value)

        return ObjectExpr3229()

    def _arrow3232(value_1: str, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, inv: Any=inv) -> IEncodable:
        class ObjectExpr3231(IEncodable):
            def Encode(self, helpers_1: IEncoderHelpers_1[Any]) -> Any:
                return helpers_1.encode_string(value_1)

        return ObjectExpr3231()

    def _arrow3234(value_3: str, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, inv: Any=inv) -> IEncodable:
        class ObjectExpr3233(IEncodable):
            def Encode(self, helpers_2: IEncoderHelpers_1[Any]) -> Any:
                return helpers_2.encode_string(value_3)

        return ObjectExpr3233()

    def _arrow3236(value_5: str, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, inv: Any=inv) -> IEncodable:
        class ObjectExpr3235(IEncodable):
            def Encode(self, helpers_3: IEncoderHelpers_1[Any]) -> Any:
                return helpers_3.encode_string(value_5)

        return ObjectExpr3235()

    def _arrow3238(value_7: str, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, inv: Any=inv) -> IEncodable:
        class ObjectExpr3237(IEncodable):
            def Encode(self, helpers_4: IEncoderHelpers_1[Any]) -> Any:
                return helpers_4.encode_string(value_7)

        return ObjectExpr3237()

    def _arrow3239(osr: OntologySourceReference, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, inv: Any=inv) -> IEncodable:
        return encoder_1(osr)

    def _arrow3240(oa: Publication, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, inv: Any=inv) -> IEncodable:
        return encoder_2(oa)

    def _arrow3241(person: Person, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, inv: Any=inv) -> IEncodable:
        return encoder_3(person)

    def _arrow3242(assay: ArcAssay, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, inv: Any=inv) -> IEncodable:
        return encoder_compressed_1(string_table, oa_table, cell_table, assay)

    def _arrow3243(study: ArcStudy, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, inv: Any=inv) -> IEncodable:
        return encoder_compressed_2(string_table, oa_table, cell_table, study)

    def _arrow3245(value_9: str, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, inv: Any=inv) -> IEncodable:
        class ObjectExpr3244(IEncodable):
            def Encode(self, helpers_5: IEncoderHelpers_1[Any]) -> Any:
                return helpers_5.encode_string(value_9)

        return ObjectExpr3244()

    def _arrow3246(comment: Comment, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, inv: Any=inv) -> IEncodable:
        return encoder_6(comment)

    values: FSharpList[tuple[str, IEncodable]] = choose(chooser, of_array([("Identifier", _arrow3230()), try_include("Title", _arrow3232, inv.Title), try_include("Description", _arrow3234, inv.Description), try_include("SubmissionDate", _arrow3236, inv.SubmissionDate), try_include("PublicReleaseDate", _arrow3238, inv.PublicReleaseDate), try_include_seq("OntologySourceReferences", _arrow3239, inv.OntologySourceReferences), try_include_seq("Publications", _arrow3240, inv.Publications), try_include_seq("Contacts", _arrow3241, inv.Contacts), try_include_seq("Assays", _arrow3242, inv.Assays), try_include_seq("Studies", _arrow3243, inv.Studies), try_include_seq("RegisteredStudyIdentifiers", _arrow3245, inv.RegisteredStudyIdentifiers), try_include_seq("Comments", _arrow3246, inv.Comments)]))
    class ObjectExpr3247(IEncodable):
        def Encode(self, helpers_6: IEncoderHelpers_1[Any], string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, inv: Any=inv) -> Any:
            def mapping_1(tupled_arg_1: tuple[str, IEncodable]) -> tuple[str, __A_]:
                return (tupled_arg_1[0], tupled_arg_1[1].Encode(helpers_6))

            arg: IEnumerable_1[tuple[str, __A_]] = map_1(mapping_1, values)
            return helpers_6.encode_object(arg)

    return ObjectExpr3247()


def decoder_compressed(string_table: Array[str], oa_table: Array[OntologyAnnotation], cell_table: Array[CompositeCell]) -> Decoder_1[ArcInvestigation]:
    def _arrow3261(get: IGetters, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table) -> ArcInvestigation:
        def _arrow3248(__unit: None=None) -> str:
            object_arg: IRequiredGetter = get.Required
            return object_arg.Field("Identifier", string)

        def _arrow3249(__unit: None=None) -> str | None:
            object_arg_1: IOptionalGetter = get.Optional
            return object_arg_1.Field("Title", string)

        def _arrow3250(__unit: None=None) -> str | None:
            object_arg_2: IOptionalGetter = get.Optional
            return object_arg_2.Field("Description", string)

        def _arrow3251(__unit: None=None) -> str | None:
            object_arg_3: IOptionalGetter = get.Optional
            return object_arg_3.Field("SubmissionDate", string)

        def _arrow3252(__unit: None=None) -> str | None:
            object_arg_4: IOptionalGetter = get.Optional
            return object_arg_4.Field("PublicReleaseDate", string)

        def _arrow3253(__unit: None=None) -> Array[OntologySourceReference] | None:
            arg_11: Decoder_1[Array[OntologySourceReference]] = resize_array(decoder_3)
            object_arg_5: IOptionalGetter = get.Optional
            return object_arg_5.Field("OntologySourceReferences", arg_11)

        def _arrow3254(__unit: None=None) -> Array[Publication] | None:
            arg_13: Decoder_1[Array[Publication]] = resize_array(decoder_4)
            object_arg_6: IOptionalGetter = get.Optional
            return object_arg_6.Field("Publications", arg_13)

        def _arrow3256(__unit: None=None) -> Array[Person] | None:
            arg_15: Decoder_1[Array[Person]] = resize_array(decoder_5)
            object_arg_7: IOptionalGetter = get.Optional
            return object_arg_7.Field("Contacts", arg_15)

        def _arrow3257(__unit: None=None) -> Array[ArcAssay] | None:
            arg_17: Decoder_1[Array[ArcAssay]] = resize_array(decoder_compressed_1(string_table, oa_table, cell_table))
            object_arg_8: IOptionalGetter = get.Optional
            return object_arg_8.Field("Assays", arg_17)

        def _arrow3258(__unit: None=None) -> Array[ArcStudy] | None:
            arg_19: Decoder_1[Array[ArcStudy]] = resize_array(decoder_compressed_2(string_table, oa_table, cell_table))
            object_arg_9: IOptionalGetter = get.Optional
            return object_arg_9.Field("Studies", arg_19)

        def _arrow3259(__unit: None=None) -> Array[str] | None:
            arg_21: Decoder_1[Array[str]] = resize_array(string)
            object_arg_10: IOptionalGetter = get.Optional
            return object_arg_10.Field("RegisteredStudyIdentifiers", arg_21)

        def _arrow3260(__unit: None=None) -> Array[Comment] | None:
            arg_23: Decoder_1[Array[Comment]] = resize_array(decoder_8)
            object_arg_11: IOptionalGetter = get.Optional
            return object_arg_11.Field("Comments", arg_23)

        return ArcInvestigation(_arrow3248(), _arrow3249(), _arrow3250(), _arrow3251(), _arrow3252(), _arrow3253(), _arrow3254(), _arrow3256(), _arrow3257(), _arrow3258(), None, None, _arrow3259(), _arrow3260())

    return object(_arrow3261)


def ROCrate_genID(i: ArcInvestigation) -> str:
    return "./"


def ROCrate_encoder(oa: ArcInvestigation) -> IEncodable:
    def chooser(tupled_arg: tuple[str, IEncodable | None], oa: Any=oa) -> tuple[str, IEncodable] | None:
        def mapping(v_1: IEncodable, tupled_arg: Any=tupled_arg) -> tuple[str, IEncodable]:
            return (tupled_arg[0], v_1)

        return map(mapping, tupled_arg[1])

    def _arrow3265(__unit: None=None, oa: Any=oa) -> IEncodable:
        value: str = ROCrate_genID(oa)
        class ObjectExpr3264(IEncodable):
            def Encode(self, helpers: IEncoderHelpers_1[Any]) -> Any:
                return helpers.encode_string(value)

        return ObjectExpr3264()

    class ObjectExpr3266(IEncodable):
        def Encode(self, helpers_1: IEncoderHelpers_1[Any], oa: Any=oa) -> Any:
            return helpers_1.encode_string("Investigation")

    class ObjectExpr3267(IEncodable):
        def Encode(self, helpers_2: IEncoderHelpers_1[Any], oa: Any=oa) -> Any:
            return helpers_2.encode_string("Investigation")

    def _arrow3269(__unit: None=None, oa: Any=oa) -> IEncodable:
        value_3: str = oa.Identifier
        class ObjectExpr3268(IEncodable):
            def Encode(self, helpers_3: IEncoderHelpers_1[Any]) -> Any:
                return helpers_3.encode_string(value_3)

        return ObjectExpr3268()

    def _arrow3271(__unit: None=None, oa: Any=oa) -> IEncodable:
        value_4: str = ArcInvestigation.FileName()
        class ObjectExpr3270(IEncodable):
            def Encode(self, helpers_4: IEncoderHelpers_1[Any]) -> Any:
                return helpers_4.encode_string(value_4)

        return ObjectExpr3270()

    def _arrow3273(value_5: str, oa: Any=oa) -> IEncodable:
        class ObjectExpr3272(IEncodable):
            def Encode(self, helpers_5: IEncoderHelpers_1[Any]) -> Any:
                return helpers_5.encode_string(value_5)

        return ObjectExpr3272()

    def _arrow3275(value_7: str, oa: Any=oa) -> IEncodable:
        class ObjectExpr3274(IEncodable):
            def Encode(self, helpers_6: IEncoderHelpers_1[Any]) -> Any:
                return helpers_6.encode_string(value_7)

        return ObjectExpr3274()

    def _arrow3277(value_9: str, oa: Any=oa) -> IEncodable:
        class ObjectExpr3276(IEncodable):
            def Encode(self, helpers_7: IEncoderHelpers_1[Any]) -> Any:
                return helpers_7.encode_string(value_9)

        return ObjectExpr3276()

    def _arrow3280(__unit: None=None, oa: Any=oa) -> IEncodable:
        def _arrow3278(__unit: None=None) -> str:
            copy_of_struct: Any = today()
            return to_string(copy_of_struct, "yyyy-MM-dd")

        value_12: str = default_arg(oa.PublicReleaseDate, _arrow3278())
        class ObjectExpr3279(IEncodable):
            def Encode(self, helpers_8: IEncoderHelpers_1[Any]) -> Any:
                return helpers_8.encode_string(value_12)

        return ObjectExpr3279()

    def _arrow3281(osr: OntologySourceReference, oa: Any=oa) -> IEncodable:
        return ROCrate_encoder_1(osr)

    def _arrow3282(oa_1: Publication, oa: Any=oa) -> IEncodable:
        return ROCrate_encoder_2(oa_1)

    def _arrow3283(oa_2: Person, oa: Any=oa) -> IEncodable:
        return ROCrate_encoder_3(oa_2)

    def _arrow3284(s: ArcStudy, oa: Any=oa) -> IEncodable:
        return ROCrate_encoder_4(None, s)

    def _arrow3285(comment: Comment, oa: Any=oa) -> IEncodable:
        return ROCrate_encoder_5(comment)

    values: FSharpList[tuple[str, IEncodable]] = choose(chooser, of_array([("@id", _arrow3265()), ("@type", ObjectExpr3266()), ("additionalType", ObjectExpr3267()), ("identifier", _arrow3269()), ("filename", _arrow3271()), try_include("title", _arrow3273, oa.Title), try_include("description", _arrow3275, oa.Description), try_include("submissionDate", _arrow3277, oa.SubmissionDate), ("publicReleaseDate", _arrow3280()), try_include_seq("ontologySourceReferences", _arrow3281, oa.OntologySourceReferences), try_include_seq("publications", _arrow3282, oa.Publications), try_include_seq("people", _arrow3283, oa.Contacts), try_include_seq("studies", _arrow3284, oa.Studies), try_include_seq("comments", _arrow3285, oa.Comments), ("@context", context_jsonvalue)]))
    class ObjectExpr3286(IEncodable):
        def Encode(self, helpers_9: IEncoderHelpers_1[Any], oa: Any=oa) -> Any:
            def mapping_1(tupled_arg_1: tuple[str, IEncodable]) -> tuple[str, __A_]:
                return (tupled_arg_1[0], tupled_arg_1[1].Encode(helpers_9))

            arg: IEnumerable_1[tuple[str, __A_]] = map_1(mapping_1, values)
            return helpers_9.encode_object(arg)

    return ObjectExpr3286()


def _arrow3298(get: IGetters) -> ArcInvestigation:
    identifier: str
    match_value: str | None
    object_arg: IOptionalGetter = get.Optional
    match_value = object_arg.Field("identifier", string)
    identifier = create_missing_identifier() if (match_value is None) else match_value
    def _arrow3287(__unit: None=None) -> FSharpList[tuple[ArcStudy, FSharpList[ArcAssay]]] | None:
        arg_3: Decoder_1[FSharpList[tuple[ArcStudy, FSharpList[ArcAssay]]]] = list_1_1(ROCrate_decoder_1)
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("studies", arg_3)

    pattern_input: tuple[FSharpList[ArcStudy], FSharpList[FSharpList[ArcAssay]]] = unzip(default_arg(_arrow3287(), empty()))
    studies_raw: FSharpList[ArcStudy] = pattern_input[0]
    def projection(a: ArcAssay) -> str:
        return a.Identifier

    class ObjectExpr3289:
        @property
        def Equals(self) -> Callable[[str, str], bool]:
            def _arrow3288(x: str, y: str) -> bool:
                return x == y

            return _arrow3288

        @property
        def GetHashCode(self) -> Callable[[str], int]:
            return string_hash

    assays: Array[ArcAssay] = list(distinct_by(projection, concat(pattern_input[1]), ObjectExpr3289()))
    studies: Array[ArcStudy] = list(studies_raw)
    def mapping(a_1: ArcStudy) -> str:
        return a_1.Identifier

    study_identifiers: Array[str] = list(map_1(mapping, studies_raw))
    def _arrow3290(__unit: None=None) -> str | None:
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("title", string)

    def _arrow3291(__unit: None=None) -> str | None:
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("description", string)

    def _arrow3292(__unit: None=None) -> str | None:
        object_arg_4: IOptionalGetter = get.Optional
        return object_arg_4.Field("submissionDate", string)

    def _arrow3293(__unit: None=None) -> str | None:
        object_arg_5: IOptionalGetter = get.Optional
        return object_arg_5.Field("publicReleaseDate", string)

    def _arrow3294(__unit: None=None) -> Array[OntologySourceReference] | None:
        arg_13: Decoder_1[Array[OntologySourceReference]] = resize_array(ROCrate_decoder_2)
        object_arg_6: IOptionalGetter = get.Optional
        return object_arg_6.Field("ontologySourceReferences", arg_13)

    def _arrow3295(__unit: None=None) -> Array[Publication] | None:
        arg_15: Decoder_1[Array[Publication]] = resize_array(ROCrate_decoder_3)
        object_arg_7: IOptionalGetter = get.Optional
        return object_arg_7.Field("publications", arg_15)

    def _arrow3296(__unit: None=None) -> Array[Person] | None:
        arg_17: Decoder_1[Array[Person]] = resize_array(ROCrate_decoder_4)
        object_arg_8: IOptionalGetter = get.Optional
        return object_arg_8.Field("people", arg_17)

    def _arrow3297(__unit: None=None) -> Array[Comment] | None:
        arg_19: Decoder_1[Array[Comment]] = resize_array(ROCrate_decoder_5)
        object_arg_9: IOptionalGetter = get.Optional
        return object_arg_9.Field("comments", arg_19)

    return ArcInvestigation(identifier, _arrow3290(), _arrow3291(), _arrow3292(), _arrow3293(), _arrow3294(), _arrow3295(), _arrow3296(), assays, studies, None, None, study_identifiers, _arrow3297())


ROCrate_decoder: Decoder_1[ArcInvestigation] = object(_arrow3298)

def ROCrate_encodeRoCrate(oa: ArcInvestigation) -> IEncodable:
    def chooser(tupled_arg: tuple[str, IEncodable | None], oa: Any=oa) -> tuple[str, IEncodable] | None:
        def mapping(v_1: IEncodable, tupled_arg: Any=tupled_arg) -> tuple[str, IEncodable]:
            return (tupled_arg[0], v_1)

        return map(mapping, tupled_arg[1])

    def _arrow3302(value: str, oa: Any=oa) -> IEncodable:
        class ObjectExpr3301(IEncodable):
            def Encode(self, helpers: IEncoderHelpers_1[Any]) -> Any:
                return helpers.encode_string(value)

        return ObjectExpr3301()

    def _arrow3304(value_2: str, oa: Any=oa) -> IEncodable:
        class ObjectExpr3303(IEncodable):
            def Encode(self, helpers_1: IEncoderHelpers_1[Any]) -> Any:
                return helpers_1.encode_string(value_2)

        return ObjectExpr3303()

    def _arrow3305(oa_1: ArcInvestigation, oa: Any=oa) -> IEncodable:
        return ROCrate_encoder(oa_1)

    values: FSharpList[tuple[str, IEncodable]] = choose(chooser, of_array([try_include("@type", _arrow3302, "CreativeWork"), try_include("@id", _arrow3304, "ro-crate-metadata.json"), try_include("about", _arrow3305, oa), ("conformsTo", conforms_to_jsonvalue), ("@context", context_jsonvalue_1)]))
    class ObjectExpr3306(IEncodable):
        def Encode(self, helpers_2: IEncoderHelpers_1[Any], oa: Any=oa) -> Any:
            def mapping_1(tupled_arg_1: tuple[str, IEncodable]) -> tuple[str, __A_]:
                return (tupled_arg_1[0], tupled_arg_1[1].Encode(helpers_2))

            arg: IEnumerable_1[tuple[str, __A_]] = map_1(mapping_1, values)
            return helpers_2.encode_object(arg)

    return ObjectExpr3306()


ISAJson_allowedFields: FSharpList[str] = of_array(["@id", "filename", "identifier", "title", "description", "submissionDate", "publicReleaseDate", "ontologySourceReferences", "publications", "people", "studies", "comments", "@type", "@context"])

def ISAJson_encoder(id_map: Any | None, inv: ArcInvestigation) -> IEncodable:
    def chooser(tupled_arg: tuple[str, IEncodable | None], id_map: Any=id_map, inv: Any=inv) -> tuple[str, IEncodable] | None:
        def mapping(v_1: IEncodable, tupled_arg: Any=tupled_arg) -> tuple[str, IEncodable]:
            return (tupled_arg[0], v_1)

        return map(mapping, tupled_arg[1])

    def _arrow3310(__unit: None=None, id_map: Any=id_map, inv: Any=inv) -> IEncodable:
        value: str = ROCrate_genID(inv)
        class ObjectExpr3309(IEncodable):
            def Encode(self, helpers: IEncoderHelpers_1[Any]) -> Any:
                return helpers.encode_string(value)

        return ObjectExpr3309()

    def _arrow3312(__unit: None=None, id_map: Any=id_map, inv: Any=inv) -> IEncodable:
        value_1: str = ArcInvestigation.FileName()
        class ObjectExpr3311(IEncodable):
            def Encode(self, helpers_1: IEncoderHelpers_1[Any]) -> Any:
                return helpers_1.encode_string(value_1)

        return ObjectExpr3311()

    def _arrow3314(__unit: None=None, id_map: Any=id_map, inv: Any=inv) -> IEncodable:
        value_2: str = inv.Identifier
        class ObjectExpr3313(IEncodable):
            def Encode(self, helpers_2: IEncoderHelpers_1[Any]) -> Any:
                return helpers_2.encode_string(value_2)

        return ObjectExpr3313()

    def _arrow3316(value_3: str, id_map: Any=id_map, inv: Any=inv) -> IEncodable:
        class ObjectExpr3315(IEncodable):
            def Encode(self, helpers_3: IEncoderHelpers_1[Any]) -> Any:
                return helpers_3.encode_string(value_3)

        return ObjectExpr3315()

    def _arrow3318(value_5: str, id_map: Any=id_map, inv: Any=inv) -> IEncodable:
        class ObjectExpr3317(IEncodable):
            def Encode(self, helpers_4: IEncoderHelpers_1[Any]) -> Any:
                return helpers_4.encode_string(value_5)

        return ObjectExpr3317()

    def _arrow3320(value_7: str, id_map: Any=id_map, inv: Any=inv) -> IEncodable:
        class ObjectExpr3319(IEncodable):
            def Encode(self, helpers_5: IEncoderHelpers_1[Any]) -> Any:
                return helpers_5.encode_string(value_7)

        return ObjectExpr3319()

    def _arrow3323(value_9: str, id_map: Any=id_map, inv: Any=inv) -> IEncodable:
        class ObjectExpr3322(IEncodable):
            def Encode(self, helpers_6: IEncoderHelpers_1[Any]) -> Any:
                return helpers_6.encode_string(value_9)

        return ObjectExpr3322()

    def _arrow3324(osr: OntologySourceReference, id_map: Any=id_map, inv: Any=inv) -> IEncodable:
        return ISAJson_encoder_1(id_map, osr)

    def _arrow3325(oa: Publication, id_map: Any=id_map, inv: Any=inv) -> IEncodable:
        return ISAJson_encoder_2(id_map, oa)

    def _arrow3326(person: Person, id_map: Any=id_map, inv: Any=inv) -> IEncodable:
        return ISAJson_encoder_3(id_map, person)

    def _arrow3327(s: ArcStudy, id_map: Any=id_map, inv: Any=inv) -> IEncodable:
        return ISAJson_encoder_4(id_map, None, s)

    def _arrow3328(comment: Comment, id_map: Any=id_map, inv: Any=inv) -> IEncodable:
        return ISAJson_encoder_5(id_map, comment)

    values: FSharpList[tuple[str, IEncodable]] = choose(chooser, of_array([("@id", _arrow3310()), ("filename", _arrow3312()), ("identifier", _arrow3314()), try_include("title", _arrow3316, inv.Title), try_include("description", _arrow3318, inv.Description), try_include("submissionDate", _arrow3320, inv.SubmissionDate), try_include("publicReleaseDate", _arrow3323, inv.PublicReleaseDate), try_include_seq("ontologySourceReferences", _arrow3324, inv.OntologySourceReferences), try_include_seq("publications", _arrow3325, inv.Publications), try_include_seq("people", _arrow3326, inv.Contacts), try_include_seq("studies", _arrow3327, inv.Studies), try_include_seq("comments", _arrow3328, inv.Comments)]))
    class ObjectExpr3329(IEncodable):
        def Encode(self, helpers_7: IEncoderHelpers_1[Any], id_map: Any=id_map, inv: Any=inv) -> Any:
            def mapping_1(tupled_arg_1: tuple[str, IEncodable]) -> tuple[str, __A_]:
                return (tupled_arg_1[0], tupled_arg_1[1].Encode(helpers_7))

            arg: IEnumerable_1[tuple[str, __A_]] = map_1(mapping_1, values)
            return helpers_7.encode_object(arg)

    return ObjectExpr3329()


def _arrow3341(get: IGetters) -> ArcInvestigation:
    identifer: str
    match_value: str | None
    object_arg: IOptionalGetter = get.Optional
    match_value = object_arg.Field("identifier", string)
    identifer = create_missing_identifier() if (match_value is None) else match_value
    def _arrow3330(__unit: None=None) -> FSharpList[tuple[ArcStudy, FSharpList[ArcAssay]]] | None:
        arg_3: Decoder_1[FSharpList[tuple[ArcStudy, FSharpList[ArcAssay]]]] = list_1_1(ISAJson_decoder_1)
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("studies", arg_3)

    pattern_input: tuple[FSharpList[ArcStudy], FSharpList[FSharpList[ArcAssay]]] = unzip(default_arg(_arrow3330(), empty()))
    studies_raw: FSharpList[ArcStudy] = pattern_input[0]
    def projection(a: ArcAssay) -> str:
        return a.Identifier

    class ObjectExpr3332:
        @property
        def Equals(self) -> Callable[[str, str], bool]:
            def _arrow3331(x: str, y: str) -> bool:
                return x == y

            return _arrow3331

        @property
        def GetHashCode(self) -> Callable[[str], int]:
            return string_hash

    assays: Array[ArcAssay] = list(distinct_by(projection, concat(pattern_input[1]), ObjectExpr3332()))
    studies: Array[ArcStudy] = list(studies_raw)
    def mapping(a_1: ArcStudy) -> str:
        return a_1.Identifier

    study_identifiers: Array[str] = list(map_1(mapping, studies_raw))
    def _arrow3333(__unit: None=None) -> str | None:
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("title", string)

    def _arrow3334(__unit: None=None) -> str | None:
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("description", string)

    def _arrow3335(__unit: None=None) -> str | None:
        object_arg_4: IOptionalGetter = get.Optional
        return object_arg_4.Field("submissionDate", string)

    def _arrow3336(__unit: None=None) -> str | None:
        object_arg_5: IOptionalGetter = get.Optional
        return object_arg_5.Field("publicReleaseDate", string)

    def _arrow3337(__unit: None=None) -> Array[OntologySourceReference] | None:
        arg_13: Decoder_1[Array[OntologySourceReference]] = resize_array(ISAJson_decoder_2)
        object_arg_6: IOptionalGetter = get.Optional
        return object_arg_6.Field("ontologySourceReferences", arg_13)

    def _arrow3338(__unit: None=None) -> Array[Publication] | None:
        arg_15: Decoder_1[Array[Publication]] = resize_array(ISAJson_decoder_3)
        object_arg_7: IOptionalGetter = get.Optional
        return object_arg_7.Field("publications", arg_15)

    def _arrow3339(__unit: None=None) -> Array[Person] | None:
        arg_17: Decoder_1[Array[Person]] = resize_array(ISAJson_decoder_4)
        object_arg_8: IOptionalGetter = get.Optional
        return object_arg_8.Field("people", arg_17)

    def _arrow3340(__unit: None=None) -> Array[Comment] | None:
        arg_19: Decoder_1[Array[Comment]] = resize_array(ISAJson_decoder_5)
        object_arg_9: IOptionalGetter = get.Optional
        return object_arg_9.Field("comments", arg_19)

    return ArcInvestigation(identifer, _arrow3333(), _arrow3334(), _arrow3335(), _arrow3336(), _arrow3337(), _arrow3338(), _arrow3339(), assays, studies, None, None, study_identifiers, _arrow3340())


ISAJson_decoder: Decoder_1[ArcInvestigation] = Decode_objectNoAdditionalProperties(ISAJson_allowedFields, _arrow3341)

__all__ = ["encoder", "decoder", "encoder_compressed", "decoder_compressed", "ROCrate_genID", "ROCrate_encoder", "ROCrate_decoder", "ROCrate_encodeRoCrate", "ISAJson_allowedFields", "ISAJson_encoder", "ISAJson_decoder"]

