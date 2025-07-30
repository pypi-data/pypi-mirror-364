from __future__ import annotations
from collections.abc import Callable
from typing import (Any, TypeVar)
from ..fable_modules.fable_library.list import (choose, of_array, FSharpList, singleton, empty)
from ..fable_modules.fable_library.option import (map, default_arg, value as value_9, bind)
from ..fable_modules.fable_library.seq import (map as map_1, to_list, delay, append, empty as empty_1, singleton as singleton_1, try_pick, length)
from ..fable_modules.fable_library.string_ import replace
from ..fable_modules.fable_library.types import Array
from ..fable_modules.fable_library.util import IEnumerable_1
from ..fable_modules.thoth_json_core.decode import (object, IRequiredGetter, string, IOptionalGetter, resize_array, IGetters, list_1 as list_1_2, map as map_2)
from ..fable_modules.thoth_json_core.encode import list_1 as list_1_1
from ..fable_modules.thoth_json_core.types import (IEncodable, IEncoderHelpers_1, Decoder_1)
from ..Core.arc_types import ArcAssay
from ..Core.comment import Comment
from ..Core.conversion import (ARCtrl_ArcTables__ArcTables_GetProcesses, ARCtrl_ArcTables__ArcTables_fromProcesses_Static_62A3309D, JsonTypes_composeTechnologyPlatform, JsonTypes_decomposeTechnologyPlatform)
from ..Core.data import Data
from ..Core.data_map import DataMap
from ..Core.Helper.collections_ import (Option_fromValueWithDefault, ResizeArray_filter)
from ..Core.Helper.identifier import (Assay_fileNameFromIdentifier, create_missing_identifier, Assay_tryIdentifierFromFileName)
from ..Core.ontology_annotation import OntologyAnnotation
from ..Core.person import Person
from ..Core.Process.material_attribute import MaterialAttribute
from ..Core.Process.process import Process
from ..Core.Process.process_sequence import (get_data, get_units, get_characteristics)
from ..Core.Table.arc_table import ArcTable
from ..Core.Table.arc_tables import ArcTables
from ..Core.Table.composite_cell import CompositeCell
from .comment import (encoder as encoder_7, decoder as decoder_4, ROCrate_encoder as ROCrate_encoder_4, ROCrate_decoder as ROCrate_decoder_3, ISAJson_encoder as ISAJson_encoder_3, ISAJson_decoder as ISAJson_decoder_2)
from .context.rocrate.isa_assay_context import context_jsonvalue
from .data import (ROCrate_encoder as ROCrate_encoder_2, ISAJson_encoder as ISAJson_encoder_1)
from .DataMap.data_map import (encoder as encoder_4, decoder as decoder_2, encoder_compressed as encoder_compressed_2, decoder_compressed as decoder_compressed_2)
from .decode import Decode_objectNoAdditionalProperties
from .encode import (try_include, try_include_seq, try_include_list)
from .idtable import encode
from .ontology_annotation import (OntologyAnnotation_encoder, OntologyAnnotation_decoder, OntologyAnnotation_ROCrate_encoderPropertyValue, OntologyAnnotation_ROCrate_encoderDefinedTerm, OntologyAnnotation_ROCrate_decoderPropertyValue, OntologyAnnotation_ROCrate_decoderDefinedTerm, OntologyAnnotation_ISAJson_encoder, OntologyAnnotation_ISAJson_decoder)
from .person import (encoder as encoder_6, decoder as decoder_3, ROCrate_encoder as ROCrate_encoder_1, ROCrate_decoder as ROCrate_decoder_2)
from .Process.assay_materials import encoder as encoder_9
from .Process.material_attribute import encoder as encoder_8
from .Process.process import (ROCrate_encoder as ROCrate_encoder_3, ROCrate_decoder as ROCrate_decoder_1, ISAJson_encoder as ISAJson_encoder_2, ISAJson_decoder as ISAJson_decoder_1)
from .Table.arc_table import (encoder as encoder_5, decoder as decoder_1, encoder_compressed as encoder_compressed_1, decoder_compressed as decoder_compressed_1)

__A_ = TypeVar("__A_")

def encoder(assay: ArcAssay) -> IEncodable:
    def chooser(tupled_arg: tuple[str, IEncodable | None], assay: Any=assay) -> tuple[str, IEncodable] | None:
        def mapping(v_1: IEncodable, tupled_arg: Any=tupled_arg) -> tuple[str, IEncodable]:
            return (tupled_arg[0], v_1)

        return map(mapping, tupled_arg[1])

    def _arrow2921(__unit: None=None, assay: Any=assay) -> IEncodable:
        value: str = assay.Identifier
        class ObjectExpr2920(IEncodable):
            def Encode(self, helpers: IEncoderHelpers_1[Any]) -> Any:
                return helpers.encode_string(value)

        return ObjectExpr2920()

    def _arrow2923(value_1: str, assay: Any=assay) -> IEncodable:
        class ObjectExpr2922(IEncodable):
            def Encode(self, helpers_1: IEncoderHelpers_1[Any]) -> Any:
                return helpers_1.encode_string(value_1)

        return ObjectExpr2922()

    def _arrow2925(value_3: str, assay: Any=assay) -> IEncodable:
        class ObjectExpr2924(IEncodable):
            def Encode(self, helpers_2: IEncoderHelpers_1[Any]) -> Any:
                return helpers_2.encode_string(value_3)

        return ObjectExpr2924()

    def _arrow2926(oa: OntologyAnnotation, assay: Any=assay) -> IEncodable:
        return OntologyAnnotation_encoder(oa)

    def _arrow2927(oa_1: OntologyAnnotation, assay: Any=assay) -> IEncodable:
        return OntologyAnnotation_encoder(oa_1)

    def _arrow2928(oa_2: OntologyAnnotation, assay: Any=assay) -> IEncodable:
        return OntologyAnnotation_encoder(oa_2)

    def _arrow2929(dm: DataMap, assay: Any=assay) -> IEncodable:
        return encoder_4(dm)

    def _arrow2930(table: ArcTable, assay: Any=assay) -> IEncodable:
        return encoder_5(table)

    def _arrow2931(person: Person, assay: Any=assay) -> IEncodable:
        return encoder_6(person)

    def _arrow2932(comment: Comment, assay: Any=assay) -> IEncodable:
        return encoder_7(comment)

    values: FSharpList[tuple[str, IEncodable]] = choose(chooser, of_array([("Identifier", _arrow2921()), try_include("Title", _arrow2923, assay.Title), try_include("Description", _arrow2925, assay.Description), try_include("MeasurementType", _arrow2926, assay.MeasurementType), try_include("TechnologyType", _arrow2927, assay.TechnologyType), try_include("TechnologyPlatform", _arrow2928, assay.TechnologyPlatform), try_include("DataMap", _arrow2929, assay.DataMap), try_include_seq("Tables", _arrow2930, assay.Tables), try_include_seq("Performers", _arrow2931, assay.Performers), try_include_seq("Comments", _arrow2932, assay.Comments)]))
    class ObjectExpr2933(IEncodable):
        def Encode(self, helpers_3: IEncoderHelpers_1[Any], assay: Any=assay) -> Any:
            def mapping_1(tupled_arg_1: tuple[str, IEncodable]) -> tuple[str, __A_]:
                return (tupled_arg_1[0], tupled_arg_1[1].Encode(helpers_3))

            arg: IEnumerable_1[tuple[str, __A_]] = map_1(mapping_1, values)
            return helpers_3.encode_object(arg)

    return ObjectExpr2933()


def _arrow2944(get: IGetters) -> ArcAssay:
    def _arrow2934(__unit: None=None) -> str:
        object_arg: IRequiredGetter = get.Required
        return object_arg.Field("Identifier", string)

    def _arrow2935(__unit: None=None) -> str | None:
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("Title", string)

    def _arrow2936(__unit: None=None) -> str | None:
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("Description", string)

    def _arrow2937(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("MeasurementType", OntologyAnnotation_decoder)

    def _arrow2938(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_4: IOptionalGetter = get.Optional
        return object_arg_4.Field("TechnologyType", OntologyAnnotation_decoder)

    def _arrow2939(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_5: IOptionalGetter = get.Optional
        return object_arg_5.Field("TechnologyPlatform", OntologyAnnotation_decoder)

    def _arrow2940(__unit: None=None) -> Array[ArcTable] | None:
        arg_13: Decoder_1[Array[ArcTable]] = resize_array(decoder_1)
        object_arg_6: IOptionalGetter = get.Optional
        return object_arg_6.Field("Tables", arg_13)

    def _arrow2941(__unit: None=None) -> DataMap | None:
        object_arg_7: IOptionalGetter = get.Optional
        return object_arg_7.Field("DataMap", decoder_2)

    def _arrow2942(__unit: None=None) -> Array[Person] | None:
        arg_17: Decoder_1[Array[Person]] = resize_array(decoder_3)
        object_arg_8: IOptionalGetter = get.Optional
        return object_arg_8.Field("Performers", arg_17)

    def _arrow2943(__unit: None=None) -> Array[Comment] | None:
        arg_19: Decoder_1[Array[Comment]] = resize_array(decoder_4)
        object_arg_9: IOptionalGetter = get.Optional
        return object_arg_9.Field("Comments", arg_19)

    return ArcAssay.create(_arrow2934(), _arrow2935(), _arrow2936(), _arrow2937(), _arrow2938(), _arrow2939(), _arrow2940(), _arrow2941(), _arrow2942(), _arrow2943())


decoder: Decoder_1[ArcAssay] = object(_arrow2944)

def encoder_compressed(string_table: Any, oa_table: Any, cell_table: Any, assay: ArcAssay) -> IEncodable:
    def chooser(tupled_arg: tuple[str, IEncodable | None], string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> tuple[str, IEncodable] | None:
        def mapping(v_1: IEncodable, tupled_arg: Any=tupled_arg) -> tuple[str, IEncodable]:
            return (tupled_arg[0], v_1)

        return map(mapping, tupled_arg[1])

    def _arrow2948(__unit: None=None, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> IEncodable:
        value: str = assay.Identifier
        class ObjectExpr2947(IEncodable):
            def Encode(self, helpers: IEncoderHelpers_1[Any]) -> Any:
                return helpers.encode_string(value)

        return ObjectExpr2947()

    def _arrow2950(value_1: str, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> IEncodable:
        class ObjectExpr2949(IEncodable):
            def Encode(self, helpers_1: IEncoderHelpers_1[Any]) -> Any:
                return helpers_1.encode_string(value_1)

        return ObjectExpr2949()

    def _arrow2952(value_3: str, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> IEncodable:
        class ObjectExpr2951(IEncodable):
            def Encode(self, helpers_2: IEncoderHelpers_1[Any]) -> Any:
                return helpers_2.encode_string(value_3)

        return ObjectExpr2951()

    def _arrow2953(oa: OntologyAnnotation, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> IEncodable:
        return OntologyAnnotation_encoder(oa)

    def _arrow2954(oa_1: OntologyAnnotation, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> IEncodable:
        return OntologyAnnotation_encoder(oa_1)

    def _arrow2955(oa_2: OntologyAnnotation, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> IEncodable:
        return OntologyAnnotation_encoder(oa_2)

    def _arrow2956(table: ArcTable, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> IEncodable:
        return encoder_compressed_1(string_table, oa_table, cell_table, table)

    def _arrow2957(dm: DataMap, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> IEncodable:
        return encoder_compressed_2(string_table, oa_table, cell_table, dm)

    def _arrow2958(person: Person, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> IEncodable:
        return encoder_6(person)

    def _arrow2959(comment: Comment, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> IEncodable:
        return encoder_7(comment)

    values: FSharpList[tuple[str, IEncodable]] = choose(chooser, of_array([("Identifier", _arrow2948()), try_include("Title", _arrow2950, assay.Title), try_include("Description", _arrow2952, assay.Description), try_include("MeasurementType", _arrow2953, assay.MeasurementType), try_include("TechnologyType", _arrow2954, assay.TechnologyType), try_include("TechnologyPlatform", _arrow2955, assay.TechnologyPlatform), try_include_seq("Tables", _arrow2956, assay.Tables), try_include("DataMap", _arrow2957, assay.DataMap), try_include_seq("Performers", _arrow2958, assay.Performers), try_include_seq("Comments", _arrow2959, assay.Comments)]))
    class ObjectExpr2960(IEncodable):
        def Encode(self, helpers_3: IEncoderHelpers_1[Any], string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> Any:
            def mapping_1(tupled_arg_1: tuple[str, IEncodable]) -> tuple[str, __A_]:
                return (tupled_arg_1[0], tupled_arg_1[1].Encode(helpers_3))

            arg: IEnumerable_1[tuple[str, __A_]] = map_1(mapping_1, values)
            return helpers_3.encode_object(arg)

    return ObjectExpr2960()


def decoder_compressed(string_table: Array[str], oa_table: Array[OntologyAnnotation], cell_table: Array[CompositeCell]) -> Decoder_1[ArcAssay]:
    def _arrow2971(get: IGetters, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table) -> ArcAssay:
        def _arrow2961(__unit: None=None) -> str:
            object_arg: IRequiredGetter = get.Required
            return object_arg.Field("Identifier", string)

        def _arrow2962(__unit: None=None) -> str | None:
            object_arg_1: IOptionalGetter = get.Optional
            return object_arg_1.Field("Title", string)

        def _arrow2963(__unit: None=None) -> str | None:
            object_arg_2: IOptionalGetter = get.Optional
            return object_arg_2.Field("Description", string)

        def _arrow2964(__unit: None=None) -> OntologyAnnotation | None:
            object_arg_3: IOptionalGetter = get.Optional
            return object_arg_3.Field("MeasurementType", OntologyAnnotation_decoder)

        def _arrow2965(__unit: None=None) -> OntologyAnnotation | None:
            object_arg_4: IOptionalGetter = get.Optional
            return object_arg_4.Field("TechnologyType", OntologyAnnotation_decoder)

        def _arrow2966(__unit: None=None) -> OntologyAnnotation | None:
            object_arg_5: IOptionalGetter = get.Optional
            return object_arg_5.Field("TechnologyPlatform", OntologyAnnotation_decoder)

        def _arrow2967(__unit: None=None) -> Array[ArcTable] | None:
            arg_13: Decoder_1[Array[ArcTable]] = resize_array(decoder_compressed_1(string_table, oa_table, cell_table))
            object_arg_6: IOptionalGetter = get.Optional
            return object_arg_6.Field("Tables", arg_13)

        def _arrow2968(__unit: None=None) -> DataMap | None:
            arg_15: Decoder_1[DataMap] = decoder_compressed_2(string_table, oa_table, cell_table)
            object_arg_7: IOptionalGetter = get.Optional
            return object_arg_7.Field("DataMap", arg_15)

        def _arrow2969(__unit: None=None) -> Array[Person] | None:
            arg_17: Decoder_1[Array[Person]] = resize_array(decoder_3)
            object_arg_8: IOptionalGetter = get.Optional
            return object_arg_8.Field("Performers", arg_17)

        def _arrow2970(__unit: None=None) -> Array[Comment] | None:
            arg_19: Decoder_1[Array[Comment]] = resize_array(decoder_4)
            object_arg_9: IOptionalGetter = get.Optional
            return object_arg_9.Field("Comments", arg_19)

        return ArcAssay.create(_arrow2961(), _arrow2962(), _arrow2963(), _arrow2964(), _arrow2965(), _arrow2966(), _arrow2967(), _arrow2968(), _arrow2969(), _arrow2970())

    return object(_arrow2971)


def ROCrate_genID(a: ArcAssay) -> str:
    match_value: str = a.Identifier
    if match_value == "":
        return "#EmptyAssay"

    else: 
        return ("assays/" + replace(match_value, " ", "_")) + "/"



def ROCrate_encoder(study_name: str | None, a: ArcAssay) -> IEncodable:
    file_name: str = Assay_fileNameFromIdentifier(a.Identifier)
    processes: FSharpList[Process] = ARCtrl_ArcTables__ArcTables_GetProcesses(a)
    data_files: FSharpList[Data] = get_data(processes)
    def chooser(tupled_arg: tuple[str, IEncodable | None], study_name: Any=study_name, a: Any=a) -> tuple[str, IEncodable] | None:
        def mapping(v_1: IEncodable, tupled_arg: Any=tupled_arg) -> tuple[str, IEncodable]:
            return (tupled_arg[0], v_1)

        return map(mapping, tupled_arg[1])

    def _arrow2975(__unit: None=None, study_name: Any=study_name, a: Any=a) -> IEncodable:
        value: str = ROCrate_genID(a)
        class ObjectExpr2974(IEncodable):
            def Encode(self, helpers: IEncoderHelpers_1[Any]) -> Any:
                return helpers.encode_string(value)

        return ObjectExpr2974()

    class ObjectExpr2976(IEncodable):
        def Encode(self, helpers_1: IEncoderHelpers_1[Any], study_name: Any=study_name, a: Any=a) -> Any:
            return helpers_1.encode_string("Assay")

    class ObjectExpr2977(IEncodable):
        def Encode(self, helpers_2: IEncoderHelpers_1[Any], study_name: Any=study_name, a: Any=a) -> Any:
            return helpers_2.encode_string("Assay")

    def _arrow2979(__unit: None=None, study_name: Any=study_name, a: Any=a) -> IEncodable:
        value_3: str = a.Identifier
        class ObjectExpr2978(IEncodable):
            def Encode(self, helpers_3: IEncoderHelpers_1[Any]) -> Any:
                return helpers_3.encode_string(value_3)

        return ObjectExpr2978()

    class ObjectExpr2980(IEncodable):
        def Encode(self, helpers_4: IEncoderHelpers_1[Any], study_name: Any=study_name, a: Any=a) -> Any:
            return helpers_4.encode_string(file_name)

    def _arrow2982(value_5: str, study_name: Any=study_name, a: Any=a) -> IEncodable:
        class ObjectExpr2981(IEncodable):
            def Encode(self, helpers_5: IEncoderHelpers_1[Any]) -> Any:
                return helpers_5.encode_string(value_5)

        return ObjectExpr2981()

    def _arrow2984(value_7: str, study_name: Any=study_name, a: Any=a) -> IEncodable:
        class ObjectExpr2983(IEncodable):
            def Encode(self, helpers_6: IEncoderHelpers_1[Any]) -> Any:
                return helpers_6.encode_string(value_7)

        return ObjectExpr2983()

    def _arrow2985(oa: OntologyAnnotation, study_name: Any=study_name, a: Any=a) -> IEncodable:
        return OntologyAnnotation_ROCrate_encoderPropertyValue(oa)

    def _arrow2986(oa_1: OntologyAnnotation, study_name: Any=study_name, a: Any=a) -> IEncodable:
        return OntologyAnnotation_ROCrate_encoderDefinedTerm(oa_1)

    def _arrow2987(oa_2: OntologyAnnotation, study_name: Any=study_name, a: Any=a) -> IEncodable:
        return OntologyAnnotation_ROCrate_encoderDefinedTerm(oa_2)

    def _arrow2988(oa_3: Person, study_name: Any=study_name, a: Any=a) -> IEncodable:
        return ROCrate_encoder_1(oa_3)

    def _arrow2989(oa_4: Data, study_name: Any=study_name, a: Any=a) -> IEncodable:
        return ROCrate_encoder_2(oa_4)

    def _arrow2991(__unit: None=None, study_name: Any=study_name, a: Any=a) -> Callable[[Process], IEncodable]:
        assay_name: str | None = a.Identifier
        def _arrow2990(oa_5: Process) -> IEncodable:
            return ROCrate_encoder_3(study_name, assay_name, oa_5)

        return _arrow2990

    def _arrow2992(comment: Comment, study_name: Any=study_name, a: Any=a) -> IEncodable:
        return ROCrate_encoder_4(comment)

    values: FSharpList[tuple[str, IEncodable]] = choose(chooser, of_array([("@id", _arrow2975()), ("@type", list_1_1(singleton(ObjectExpr2976()))), ("additionalType", ObjectExpr2977()), ("identifier", _arrow2979()), ("filename", ObjectExpr2980()), try_include("title", _arrow2982, a.Title), try_include("description", _arrow2984, a.Description), try_include("measurementType", _arrow2985, a.MeasurementType), try_include("technologyType", _arrow2986, a.TechnologyType), try_include("technologyPlatform", _arrow2987, a.TechnologyPlatform), try_include_seq("performers", _arrow2988, a.Performers), try_include_list("dataFiles", _arrow2989, data_files), try_include_list("processSequence", _arrow2991(), processes), try_include_seq("comments", _arrow2992, a.Comments), ("@context", context_jsonvalue)]))
    class ObjectExpr2993(IEncodable):
        def Encode(self, helpers_7: IEncoderHelpers_1[Any], study_name: Any=study_name, a: Any=a) -> Any:
            def mapping_1(tupled_arg_1: tuple[str, IEncodable]) -> tuple[str, __A_]:
                return (tupled_arg_1[0], tupled_arg_1[1].Encode(helpers_7))

            arg: IEnumerable_1[tuple[str, __A_]] = map_1(mapping_1, values)
            return helpers_7.encode_object(arg)

    return ObjectExpr2993()


def _arrow3003(get: IGetters) -> ArcAssay:
    def _arrow2994(__unit: None=None) -> str | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("identifier", string)

    identifier: str = default_arg(_arrow2994(), create_missing_identifier())
    def mapping(arg_4: FSharpList[Process]) -> Array[ArcTable]:
        a: ArcTables = ARCtrl_ArcTables__ArcTables_fromProcesses_Static_62A3309D(arg_4)
        return a.Tables

    def _arrow2995(__unit: None=None) -> FSharpList[Process] | None:
        arg_3: Decoder_1[FSharpList[Process]] = list_1_2(ROCrate_decoder_1)
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("processSequence", arg_3)

    tables: Array[ArcTable] | None = map(mapping, _arrow2995())
    def _arrow2996(__unit: None=None) -> str | None:
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("title", string)

    def _arrow2997(__unit: None=None) -> str | None:
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("description", string)

    def _arrow2998(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_4: IOptionalGetter = get.Optional
        return object_arg_4.Field("measurementType", OntologyAnnotation_ROCrate_decoderPropertyValue)

    def _arrow2999(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_5: IOptionalGetter = get.Optional
        return object_arg_5.Field("technologyType", OntologyAnnotation_ROCrate_decoderDefinedTerm)

    def _arrow3000(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_6: IOptionalGetter = get.Optional
        return object_arg_6.Field("technologyPlatform", OntologyAnnotation_ROCrate_decoderDefinedTerm)

    def _arrow3001(__unit: None=None) -> Array[Person] | None:
        arg_16: Decoder_1[Array[Person]] = resize_array(ROCrate_decoder_2)
        object_arg_7: IOptionalGetter = get.Optional
        return object_arg_7.Field("performers", arg_16)

    def _arrow3002(__unit: None=None) -> Array[Comment] | None:
        arg_18: Decoder_1[Array[Comment]] = resize_array(ROCrate_decoder_3)
        object_arg_8: IOptionalGetter = get.Optional
        return object_arg_8.Field("comments", arg_18)

    return ArcAssay(identifier, _arrow2996(), _arrow2997(), _arrow2998(), _arrow2999(), _arrow3000(), tables, None, _arrow3001(), _arrow3002())


ROCrate_decoder: Decoder_1[ArcAssay] = object(_arrow3003)

def ISAJson_encoder(study_name: str | None, id_map: Any | None, a: ArcAssay) -> IEncodable:
    def f(a_1: ArcAssay, study_name: Any=study_name, id_map: Any=id_map, a: Any=a) -> IEncodable:
        file_name: str = Assay_fileNameFromIdentifier(a_1.Identifier)
        processes: FSharpList[Process] = ARCtrl_ArcTables__ArcTables_GetProcesses(a_1)
        def encoder_1(oa: OntologyAnnotation, a_1: Any=a_1) -> IEncodable:
            return OntologyAnnotation_ISAJson_encoder(id_map, oa)

        encoded_units: tuple[str, IEncodable | None] = try_include_list("unitCategories", encoder_1, get_units(processes))
        def encoder_2(value_1: MaterialAttribute, a_1: Any=a_1) -> IEncodable:
            return encoder_8(id_map, value_1)

        encoded_characteristics: tuple[str, IEncodable | None] = try_include_list("characteristicCategories", encoder_2, get_characteristics(processes))
        def _arrow3004(ps: FSharpList[Process], a_1: Any=a_1) -> IEncodable:
            return encoder_9(id_map, ps)

        encoded_materials: tuple[str, IEncodable | None] = try_include("materials", _arrow3004, Option_fromValueWithDefault(empty(), processes))
        def encoder_3(oa_1: Data, a_1: Any=a_1) -> IEncodable:
            return ISAJson_encoder_1(id_map, oa_1)

        encoced_data_files: tuple[str, IEncodable | None] = try_include_list("dataFiles", encoder_3, get_data(processes))
        units: FSharpList[OntologyAnnotation] = get_units(processes)
        def _arrow3007(__unit: None=None, a_1: Any=a_1) -> IEnumerable_1[Comment]:
            def _arrow3006(__unit: None=None) -> IEnumerable_1[Comment]:
                def _arrow3005(__unit: None=None) -> IEnumerable_1[Comment]:
                    return singleton_1(Comment.create("description", value_9(a_1.Description))) if (a_1.Description is not None) else empty_1()

                return append(singleton_1(Comment.create("title", value_9(a_1.Title))) if (a_1.Title is not None) else empty_1(), delay(_arrow3005))

            return append(a_1.Comments if (len(a_1.Comments) > 0) else empty_1(), delay(_arrow3006))

        comments: FSharpList[Comment] = to_list(delay(_arrow3007))
        def chooser(tupled_arg: tuple[str, IEncodable | None], a_1: Any=a_1) -> tuple[str, IEncodable] | None:
            def mapping_1(v_1: IEncodable, tupled_arg: Any=tupled_arg) -> tuple[str, IEncodable]:
                return (tupled_arg[0], v_1)

            return map(mapping_1, tupled_arg[1])

        class ObjectExpr3009(IEncodable):
            def Encode(self, helpers: IEncoderHelpers_1[Any], a_1: Any=a_1) -> Any:
                return helpers.encode_string(file_name)

        def _arrow3011(value_5: str, a_1: Any=a_1) -> IEncodable:
            class ObjectExpr3010(IEncodable):
                def Encode(self, helpers_1: IEncoderHelpers_1[Any]) -> Any:
                    return helpers_1.encode_string(value_5)

            return ObjectExpr3010()

        def _arrow3012(oa_2: OntologyAnnotation, a_1: Any=a_1) -> IEncodable:
            return OntologyAnnotation_ISAJson_encoder(id_map, oa_2)

        def _arrow3013(oa_3: OntologyAnnotation, a_1: Any=a_1) -> IEncodable:
            return OntologyAnnotation_ISAJson_encoder(id_map, oa_3)

        def _arrow3015(value_7: str, a_1: Any=a_1) -> IEncodable:
            class ObjectExpr3014(IEncodable):
                def Encode(self, helpers_2: IEncoderHelpers_1[Any]) -> Any:
                    return helpers_2.encode_string(value_7)

            return ObjectExpr3014()

        def mapping(tp: OntologyAnnotation, a_1: Any=a_1) -> str:
            return JsonTypes_composeTechnologyPlatform(tp)

        def _arrow3017(__unit: None=None, a_1: Any=a_1) -> Callable[[Process], IEncodable]:
            assay_name: str | None = a_1.Identifier
            def _arrow3016(oa_4: Process) -> IEncodable:
                return ISAJson_encoder_2(study_name, assay_name, id_map, oa_4)

            return _arrow3016

        def _arrow3018(comment: Comment, a_1: Any=a_1) -> IEncodable:
            return ISAJson_encoder_3(id_map, comment)

        values: FSharpList[tuple[str, IEncodable]] = choose(chooser, of_array([("filename", ObjectExpr3009()), try_include("@id", _arrow3011, ROCrate_genID(a_1)), try_include("measurementType", _arrow3012, a_1.MeasurementType), try_include("technologyType", _arrow3013, a_1.TechnologyType), try_include("technologyPlatform", _arrow3015, map(mapping, a_1.TechnologyPlatform)), encoced_data_files, encoded_materials, encoded_characteristics, encoded_units, try_include_list("processSequence", _arrow3017(), processes), try_include_seq("comments", _arrow3018, comments)]))
        class ObjectExpr3019(IEncodable):
            def Encode(self, helpers_3: IEncoderHelpers_1[Any], a_1: Any=a_1) -> Any:
                def mapping_2(tupled_arg_1: tuple[str, IEncodable]) -> tuple[str, __A_]:
                    return (tupled_arg_1[0], tupled_arg_1[1].Encode(helpers_3))

                arg: IEnumerable_1[tuple[str, __A_]] = map_1(mapping_2, values)
                return helpers_3.encode_object(arg)

        return ObjectExpr3019()

    if id_map is not None:
        def _arrow3020(a_2: ArcAssay, study_name: Any=study_name, id_map: Any=id_map, a: Any=a) -> str:
            return ROCrate_genID(a_2)

        return encode(_arrow3020, f, a, id_map)

    else: 
        return f(a)



ISAJson_allowedFields: FSharpList[str] = of_array(["@id", "filename", "measurementType", "technologyType", "technologyPlatform", "dataFiles", "materials", "characteristicCategories", "unitCategories", "processSequence", "comments", "@type", "@context"])

def _arrow3026(get: IGetters) -> ArcAssay:
    def _arrow3021(__unit: None=None) -> str | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("filename", string)

    identifier: str = default_arg(bind(Assay_tryIdentifierFromFileName, _arrow3021()), create_missing_identifier())
    def mapping(arg_4: FSharpList[Process]) -> Array[ArcTable]:
        a: ArcTables = ARCtrl_ArcTables__ArcTables_fromProcesses_Static_62A3309D(arg_4)
        return a.Tables

    def _arrow3022(__unit: None=None) -> FSharpList[Process] | None:
        arg_3: Decoder_1[FSharpList[Process]] = list_1_2(ISAJson_decoder_1)
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("processSequence", arg_3)

    tables: Array[ArcTable] | None = map(mapping, _arrow3022())
    comments: Array[Comment] | None
    arg_6: Decoder_1[Array[Comment]] = resize_array(ISAJson_decoder_2)
    object_arg_2: IOptionalGetter = get.Optional
    comments = object_arg_2.Field("comments", arg_6)
    def binder(c: Array[Comment]) -> str | None:
        def chooser(x: Comment, c: Any=c) -> str | None:
            if (value_9(x.Name) == "title") if (x.Name is not None) else False:
                return x.Value

            else: 
                return None


        return try_pick(chooser, c)

    title: str | None = bind(binder, comments)
    def binder_1(c_1: Array[Comment]) -> str | None:
        def chooser_1(x_1: Comment, c_1: Any=c_1) -> str | None:
            if (value_9(x_1.Name) == "description") if (x_1.Name is not None) else False:
                return x_1.Value

            else: 
                return None


        return try_pick(chooser_1, c_1)

    description: str | None = bind(binder_1, comments)
    def binder_2(c_2: Array[Comment]) -> Array[Comment] | None:
        def f(x_2: Comment, c_2: Any=c_2) -> bool:
            if x_2.Name is None:
                return True

            elif value_9(x_2.Name) != "title":
                return value_9(x_2.Name) != "description"

            else: 
                return False


        match_value: Array[Comment] = ResizeArray_filter(f, c_2)
        if length(match_value) == 0:
            return None

        else: 
            return match_value


    comments_1: Array[Comment] | None = bind(binder_2, comments)
    def _arrow3023(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("measurementType", OntologyAnnotation_ISAJson_decoder)

    def _arrow3024(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_4: IOptionalGetter = get.Optional
        return object_arg_4.Field("technologyType", OntologyAnnotation_ISAJson_decoder)

    def _arrow3025(__unit: None=None) -> OntologyAnnotation | None:
        arg_12: Decoder_1[OntologyAnnotation] = map_2(JsonTypes_decomposeTechnologyPlatform, string)
        object_arg_5: IOptionalGetter = get.Optional
        return object_arg_5.Field("technologyPlatform", arg_12)

    return ArcAssay(identifier, title, description, _arrow3023(), _arrow3024(), _arrow3025(), tables, None, None, comments_1)


ISAJson_decoder: Decoder_1[ArcAssay] = Decode_objectNoAdditionalProperties(ISAJson_allowedFields, _arrow3026)

__all__ = ["encoder", "decoder", "encoder_compressed", "decoder_compressed", "ROCrate_genID", "ROCrate_encoder", "ROCrate_decoder", "ISAJson_encoder", "ISAJson_allowedFields", "ISAJson_decoder"]

