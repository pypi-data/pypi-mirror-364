
"""Interpreter for interacting with a gRPC Stub class."""

import grpc
import threading
import warnings

import nirfmxinstr.enums as enums
import nirfmxinstr.errors as errors
import nirfmxinstr.internal.nirfmxinstr_pb2 as grpc_types
import nirfmxinstr.internal.nirfmxinstr_pb2_grpc as nirfmxinstr_grpc
import nirfmxinstr.internal.session_pb2 as session_grpc_types


class GrpcStubInterpreter(object):
    '''Interpreter for interacting with a gRPC Stub class'''

    def __init__(self, grpc_options):
        self._grpc_options = grpc_options
        self._lock = threading.RLock() #TODO: Do we need this lock?
        self._client = nirfmxinstr_grpc.NiRFmxInstrStub(grpc_options.grpc_channel)
        self.set_session_handle()

    def set_session_handle(self, value=session_grpc_types.Session()):
        self._vi = value

    def get_session_handle(self):
        return self._vi

    def _invoke(self, func, request, metadata=None):
        try:
            response = func(request, metadata=metadata)
            error_code = response.status
            error_message = ''
        except grpc.RpcError as rpc_error:
            error_code = None
            error_message = rpc_error.details()
            for entry in rpc_error.trailing_metadata() or []:
                if entry.key == 'ni-error':
                    value = entry.value if isinstance(entry.value, str) else entry.value.decode('utf-8')
                    try:
                        error_code = int(value)
                    except ValueError:
                        error_message += f'\nError status: {value}'

            grpc_error = rpc_error.code()
            if grpc_error == grpc.StatusCode.NOT_FOUND:
                raise errors.DriverTooOldError() from None
            elif grpc_error == grpc.StatusCode.INVALID_ARGUMENT:
                raise ValueError(error_message) from None
            elif grpc_error == grpc.StatusCode.UNAVAILABLE:
                error_message = 'Failed to connect to server'
            elif grpc_error == grpc.StatusCode.UNIMPLEMENTED:
                error_message = (
                    'This operation is not supported by the NI gRPC Device Server being used. Upgrade NI gRPC Device Server.'
                )

            if error_code is None:
                raise errors.RpcError(grpc_error, error_message) from None

        if error_code < 0:
            raise errors.DriverError(error_code, error_message)
        #TODO: Check warning workflow
        
        return response


    def set_attribute_i8(self, selector_string, attribute_id, attr_val):
        response = self._invoke(
            self._client.SetAttributeI8,
            grpc_types.SetAttributeI8Request(self._vi, selector_string, attribute_id, attr_val)
        )
        return response.error_code

    def get_attribute_i8(self, selector_string, attribute_id):
        response = self._invoke(
            self._client.GetAttributeI8,
            grpc_types.GetAttributeI8Request(self._vi, selector_string, attribute_id)
        )
        return response.attr_val, response.error_code

    def set_attribute_i8_array(self, selector_string, attribute_id, attr_val):
        response = self._invoke(
            self._client.SetAttributeI8Array,
            grpc_types.SetAttributeI8ArrayRequest(self._vi, selector_string, attribute_id, attr_val)
        )
        return response.error_code

    def get_attribute_i8_array(self, selector_string, attribute_id, attr_val):
        response = self._invoke(
            self._client.GetAttributeI8Array,
            grpc_types.GetAttributeI8ArrayRequest(self._vi, selector_string, attribute_id, attr_val)
        )
        return response.attr_val_array, response.error_code

    def set_attribute_i16(self, selector_string, attribute_id, attr_val):
        response = self._invoke(
            self._client.SetAttributeI16,
            grpc_types.SetAttributeI16Request(self._vi, selector_string, attribute_id, attr_val)
        )
        return response.error_code

    def get_attribute_i16(self, selector_string, attribute_id):
        response = self._invoke(
            self._client.GetAttributeI16,
            grpc_types.GetAttributeI16Request(self._vi, selector_string, attribute_id)
        )
        return response.attr_val, response.error_code

    def set_attribute_i32(self, selector_string, attribute_id, attr_val):
        response = self._invoke(
            self._client.SetAttributeI32,
            grpc_types.SetAttributeI32Request(self._vi, selector_string, attribute_id, attr_val)
        )
        return response.error_code

    def get_attribute_i32(self, selector_string, attribute_id):
        response = self._invoke(
            self._client.GetAttributeI32,
            grpc_types.GetAttributeI32Request(self._vi, selector_string, attribute_id)
        )
        return response.attr_val, response.error_code

    def set_attribute_i32_array(self, selector_string, attribute_id, attr_val):
        response = self._invoke(
            self._client.SetAttributeI32Array,
            grpc_types.SetAttributeI32ArrayRequest(self._vi, selector_string, attribute_id, attr_val)
        )
        return response.error_code

    def get_attribute_i32_array(self, selector_string, attribute_id, attr_val):
        response = self._invoke(
            self._client.GetAttributeI32Array,
            grpc_types.GetAttributeI32ArrayRequest(self._vi, selector_string, attribute_id, attr_val)
        )
        return response.attr_val_array, response.error_code

    def set_attribute_i64(self, selector_string, attribute_id, attr_val):
        response = self._invoke(
            self._client.SetAttributeI64,
            grpc_types.SetAttributeI64Request(self._vi, selector_string, attribute_id, attr_val)
        )
        return response.error_code

    def get_attribute_i64(self, selector_string, attribute_id):
        response = self._invoke(
            self._client.GetAttributeI64,
            grpc_types.GetAttributeI64Request(self._vi, selector_string, attribute_id)
        )
        return response.attr_val, response.error_code

    def set_attribute_i64_array(self, selector_string, attribute_id, attr_val):
        response = self._invoke(
            self._client.SetAttributeI64Array,
            grpc_types.SetAttributeI64ArrayRequest(self._vi, selector_string, attribute_id, attr_val)
        )
        return response.error_code

    def get_attribute_i64_array(self, selector_string, attribute_id, attr_val):
        response = self._invoke(
            self._client.GetAttributeI64Array,
            grpc_types.GetAttributeI64ArrayRequest(self._vi, selector_string, attribute_id, attr_val)
        )
        return response.attr_val_array, response.error_code

    def set_attribute_u8(self, selector_string, attribute_id, attr_val):
        response = self._invoke(
            self._client.SetAttributeU8,
            grpc_types.SetAttributeU8Request(self._vi, selector_string, attribute_id, attr_val)
        )
        return response.error_code

    def get_attribute_u8(self, selector_string, attribute_id):
        response = self._invoke(
            self._client.GetAttributeU8,
            grpc_types.GetAttributeU8Request(self._vi, selector_string, attribute_id)
        )
        return response.attr_val, response.error_code

    def set_attribute_u8_array(self, selector_string, attribute_id, attr_val):
        response = self._invoke(
            self._client.SetAttributeU8Array,
            grpc_types.SetAttributeU8ArrayRequest(self._vi, selector_string, attribute_id, attr_val)
        )
        return response.error_code

    def get_attribute_u8_array(self, selector_string, attribute_id, attr_val):
        response = self._invoke(
            self._client.GetAttributeU8Array,
            grpc_types.GetAttributeU8ArrayRequest(self._vi, selector_string, attribute_id, attr_val)
        )
        return response.attr_val_array, response.error_code

    def set_attribute_u16(self, selector_string, attribute_id, attr_val):
        response = self._invoke(
            self._client.SetAttributeU16,
            grpc_types.SetAttributeU16Request(self._vi, selector_string, attribute_id, attr_val)
        )
        return response.error_code

    def get_attribute_u16(self, selector_string, attribute_id):
        response = self._invoke(
            self._client.GetAttributeU16,
            grpc_types.GetAttributeU16Request(self._vi, selector_string, attribute_id)
        )
        return response.attr_val, response.error_code

    def set_attribute_u32(self, selector_string, attribute_id, attr_val):
        response = self._invoke(
            self._client.SetAttributeU32,
            grpc_types.SetAttributeU32Request(self._vi, selector_string, attribute_id, attr_val)
        )
        return response.error_code

    def get_attribute_u32(self, selector_string, attribute_id):
        response = self._invoke(
            self._client.GetAttributeU32,
            grpc_types.GetAttributeU32Request(self._vi, selector_string, attribute_id)
        )
        return response.attr_val, response.error_code

    def set_attribute_u32_array(self, selector_string, attribute_id, attr_val):
        response = self._invoke(
            self._client.SetAttributeU32Array,
            grpc_types.SetAttributeU32ArrayRequest(self._vi, selector_string, attribute_id, attr_val)
        )
        return response.error_code

    def get_attribute_u32_array(self, selector_string, attribute_id, attr_val):
        response = self._invoke(
            self._client.GetAttributeU32Array,
            grpc_types.GetAttributeU32ArrayRequest(self._vi, selector_string, attribute_id, attr_val)
        )
        return response.attr_val_array, response.error_code

    def set_attribute_u64_array(self, selector_string, attribute_id, attr_val):
        response = self._invoke(
            self._client.SetAttributeU64Array,
            grpc_types.SetAttributeU64ArrayRequest(self._vi, selector_string, attribute_id, attr_val)
        )
        return response.error_code

    def get_attribute_u64_array(self, selector_string, attribute_id, attr_val):
        response = self._invoke(
            self._client.GetAttributeU64Array,
            grpc_types.GetAttributeU64ArrayRequest(self._vi, selector_string, attribute_id, attr_val)
        )
        return response.attr_val_array, response.error_code

    def set_attribute_f32(self, selector_string, attribute_id, attr_val):
        response = self._invoke(
            self._client.SetAttributeF32,
            grpc_types.SetAttributeF32Request(self._vi, selector_string, attribute_id, attr_val)
        )
        return response.error_code

    def get_attribute_f32(self, selector_string, attribute_id):
        response = self._invoke(
            self._client.GetAttributeF32,
            grpc_types.GetAttributeF32Request(self._vi, selector_string, attribute_id)
        )
        return response.attr_val, response.error_code

    def set_attribute_f32_array(self, selector_string, attribute_id, attr_val):
        response = self._invoke(
            self._client.SetAttributeF32Array,
            grpc_types.SetAttributeF32ArrayRequest(self._vi, selector_string, attribute_id, attr_val)
        )
        return response.error_code

    def get_attribute_f32_array(self, selector_string, attribute_id, attr_val):
        response = self._invoke(
            self._client.GetAttributeF32Array,
            grpc_types.GetAttributeF32ArrayRequest(self._vi, selector_string, attribute_id, attr_val)
        )
        return response.attr_val_array, response.error_code

    def set_attribute_f64(self, selector_string, attribute_id, attr_val):
        response = self._invoke(
            self._client.SetAttributeF64,
            grpc_types.SetAttributeF64Request(self._vi, selector_string, attribute_id, attr_val)
        )
        return response.error_code

    def get_attribute_f64(self, selector_string, attribute_id):
        response = self._invoke(
            self._client.GetAttributeF64,
            grpc_types.GetAttributeF64Request(self._vi, selector_string, attribute_id)
        )
        return response.attr_val, response.error_code

    def set_attribute_f64_array(self, selector_string, attribute_id, attr_val):
        response = self._invoke(
            self._client.SetAttributeF64Array,
            grpc_types.SetAttributeF64ArrayRequest(self._vi, selector_string, attribute_id, attr_val)
        )
        return response.error_code

    def get_attribute_f64_array(self, selector_string, attribute_id, attr_val):
        response = self._invoke(
            self._client.GetAttributeF64Array,
            grpc_types.GetAttributeF64ArrayRequest(self._vi, selector_string, attribute_id, attr_val)
        )
        return response.attr_val_array, response.error_code

    def set_attribute_nicomplexsingle_array(self, selector_string, attribute_id, attr_val):
        response = self._invoke(
            self._client.SetAttributeNIComplexSingleArray,
            grpc_types.SetAttributeNIComplexSingleArrayRequest(self._vi, selector_string, attribute_id, attr_val)
        )
        return response.error_code

    def get_attribute_nicomplexsingle_array(self, selector_string, attribute_id, attr_val):
        response = self._invoke(
            self._client.GetAttributeNIComplexSingleArray,
            grpc_types.GetAttributeNIComplexSingleArrayRequest(self._vi, selector_string, attribute_id, attr_val)
        )
        return response.attr_val_array, response.error_code

    def set_attribute_nicomplexdouble_array(self, selector_string, attribute_id, attr_val):
        response = self._invoke(
            self._client.SetAttributeNIComplexDoubleArray,
            grpc_types.SetAttributeNIComplexDoubleArrayRequest(self._vi, selector_string, attribute_id, attr_val)
        )
        return response.error_code

    def get_attribute_nicomplexdouble_array(self, selector_string, attribute_id, attr_val):
        response = self._invoke(
            self._client.GetAttributeNIComplexDoubleArray,
            grpc_types.GetAttributeNIComplexDoubleArrayRequest(self._vi, selector_string, attribute_id, attr_val)
        )
        return response.attr_val_array, response.error_code

    def set_attribute_string(self, selector_string, attribute_id, attr_val):
        response = self._invoke(
            self._client.SetAttributeString,
            grpc_types.SetAttributeStringRequest(self._vi, selector_string, attribute_id, attr_val)
        )
        return response.error_code

    def get_attribute_string(self, selector_string, attribute_id, attr_val):
        response = self._invoke(
            self._client.GetAttributeString,
            grpc_types.GetAttributeStringRequest(self._vi, selector_string, attribute_id, attr_val)
        )
        return response.attr_val_array, response.error_code

    def check_acquisition_status(self):
        response = self._invoke(
            self._client.CheckAcquisitionStatus,
            grpc_types.CheckAcquisitionStatusRequest(self)
        )
        return bool(response.done), response.status

    def configure_external_attenuation_table(self, selector_string, table_name, frequency, external_attenuation):
        response = self._invoke(
            self._client.CfgExternalAttenuationTable,
            grpc_types.CfgExternalAttenuationTableRequest(self._vi, selector_string, table_name, frequency, external_attenuation)
        )
        return response.status

    def select_active_external_attenuation_table(self, selector_string, table_name):
        response = self._invoke(
            self._client.SelectActiveExternalAttenuationTable,
            grpc_types.SelectActiveExternalAttenuationTableRequest(self._vi, selector_string, table_name)
        )
        return response.status

    def delete_external_attenuation_table(self, selector_string, table_name):
        response = self._invoke(
            self._client.DeleteExternalAttenuationTable,
            grpc_types.DeleteExternalAttenuationTableRequest(self._vi, selector_string, table_name)
        )
        return response.status

    def delete_all_external_attenuation_tables(self, selector_string):
        response = self._invoke(
            self._client.DeleteAllExternalAttenuationTables,
            grpc_types.DeleteAllExternalAttenuationTablesRequest(self._vi, selector_string)
        )
        return response.status

    def enable_calibration_plane(self, selector_string):
        response = self._invoke(
            self._client.EnableCalibrationPlane,
            grpc_types.EnableCalibrationPlaneRequest(self._vi, selector_string)
        )
        return response.status

    def disable_calibration_plane(self, selector_string):
        response = self._invoke(
            self._client.DisableCalibrationPlane,
            grpc_types.DisableCalibrationPlaneRequest(self._vi, selector_string)
        )
        return response.status

    def check_if_signal_exists(self, signal_name):
        response = self._invoke(
            self._client.CheckIfSignalConfigurationExists,
            grpc_types.CheckIfSignalConfigurationExistsRequest(self._vi, signal_name)
        )
        return bool(response.signal_configuration_exists), enums.Personalities(response.personality), response.status

    def load_s_parameter_external_attenuation_table_from_s2p_file(self, selector_string, table_name, s2p_file_path, s_parameter_orientation):
        response = self._invoke(
            self._client.LoadSParameterExternalAttenuationTableFromS2PFile,
            grpc_types.LoadSParameterExternalAttenuationTableFromS2PFileRequest(self._vi, selector_string, table_name, s2p_file_path, s_parameter_orientation)
        )
        return response.status

    def configure_external_attenuation_interpolation_nearest(self, selector_string, table_name):
        response = self._invoke(
            self._client.CfgExternalAttenuationInterpolationNearest,
            grpc_types.CfgExternalAttenuationInterpolationNearestRequest(self._vi, selector_string, table_name)
        )
        return response.status

    def configure_external_attenuation_interpolation_linear(self, selector_string, table_name, format):
        response = self._invoke(
            self._client.CfgExternalAttenuationInterpolationLinear,
            grpc_types.CfgExternalAttenuationInterpolationLinearRequest(self._vi, selector_string, table_name, format)
        )
        return response.status

    def configure_external_attenuation_interpolation_spline(self, selector_string, table_name):
        response = self._invoke(
            self._client.CfgExternalAttenuationInterpolationSpline,
            grpc_types.CfgExternalAttenuationInterpolationSplineRequest(self._vi, selector_string, table_name)
        )
        return response.status

    def configure_s_parameter_external_attenuation_type(self, selector_string, s_parameter_type):
        response = self._invoke(
            self._client.CfgSParameterExternalAttenuationType,
            grpc_types.CfgSParameterExternalAttenuationTypeRequest(self._vi, selector_string, s_parameter_type)
        )
        return response.status

    def send_software_edge_start_trigger(self, selector_string):
        response = self._invoke(
            self._client.SendSoftwareEdgeStartTrigger,
            grpc_types.SendSoftwareEdgeStartTriggerRequest(self._vi, selector_string)
        )
        return response.status

    def send_software_edge_advance_trigger(self, selector_string):
        response = self._invoke(
            self._client.SendSoftwareEdgeAdvanceTrigger,
            grpc_types.SendSoftwareEdgeAdvanceTriggerRequest(self._vi, selector_string)
        )
        return response.status

    def configure_frequency_reference(self, selector_string, frequency_reference_source, frequency_reference_frequency):
        response = self._invoke(
            self._client.CfgFrequencyReference,
            grpc_types.CfgFrequencyReferenceRequest(self._vi, selector_string, frequency_reference_source, frequency_reference_frequency)
        )
        return response.status

    def configure_mechanical_attenuation(self, selector_string, mechanical_attenuation_auto, mechanical_attenuation_value):
        response = self._invoke(
            self._client.CfgMechanicalAttenuation,
            grpc_types.CfgMechanicalAttenuationRequest(self._vi, selector_string, mechanical_attenuation_auto, mechanical_attenuation_value)
        )
        return response.status

    def configure_rf_attenuation(self, selector_string, attenuation_auto, attenuation_value):
        response = self._invoke(
            self._client.CfgRFAttenuation,
            grpc_types.CfgRFAttenuationRequest(self._vi, selector_string, attenuation_auto, attenuation_value)
        )
        return response.status

    def wait_for_acquisition_complete(self, selector_string, timeout):
        response = self._invoke(
            self._client.WaitForAcquisitionComplete,
            grpc_types.WaitForAcquisitionCompleteRequest(self._vi, selector_string, timeout)
        )
        return response.status

    def reset_to_default(self, selector_string):
        response = self._invoke(
            self._client.ResetToDefault,
            grpc_types.ResetToDefaultRequest(self._vi, selector_string)
        )
        return response.status

    def reset_driver(self, selector_string):
        response = self._invoke(
            self._client.ResetDriver,
            grpc_types.ResetDriverRequest(self._vi, selector_string)
        )
        return response.status

    def save_all_configurations(self, file_path):
        response = self._invoke(
            self._client.SaveAllConfigurations,
            grpc_types.SaveAllConfigurationsRequest(self._vi, file_path)
        )
        return response.status

    def reset_entire_session(self):
        response = self._invoke(
            self._client.ResetEntireSession,
            grpc_types.ResetEntireSessionRequest(self)
        )
        return response.status

    def export_signal(self, export_signal_source, export_signal_output_terminal):
        response = self._invoke(
            self._client.ExportSignal,
            grpc_types.ExportSignalRequest(self._vi, export_signal_source, export_signal_output_terminal)
        )
        return response.status

    def self_calibrate(self, selector_string, steps_to_omit):
        response = self._invoke(
            self._client.SelfCalibrate,
            grpc_types.SelfCalibrateRequest(self._vi, selector_string, steps_to_omit)
        )
        return response.status

    def self_calibrate_range(self, selector_string, steps_to_omit, minimum_frequency, maximum_frequency, minimum_reference_level, maximum_reference_level):
        response = self._invoke(
            self._client.SelfCalibrateRange,
            grpc_types.SelfCalibrateRangeRequest(self._vi, selector_string, steps_to_omit, minimum_frequency, maximum_frequency, minimum_reference_level, maximum_reference_level)
        )
        return response.status

    def load_configurations(self, file_path):
        response = self._invoke(
            self._client.LoadConfigurations,
            grpc_types.LoadConfigurationsRequest(self._vi, file_path)
        )
        return response.status

    def is_self_calibrate_valid(self, selector_string):
        response = self._invoke(
            self._client.IsSelfCalibrateValid,
            grpc_types.IsSelfCalibrateValidRequest(self._vi, selector_string)
        )
        return response.self_calibrate_valid, enums.SelfCalibrateSteps(response.valid_steps), response.status

    def reset_attribute(self, selector_string, attribute_id):
        response = self._invoke(
            self._client.ResetAttribute,
            grpc_types.ResetAttributeRequest(self._vi, selector_string, attribute_id)
        )
        return response.status

    def create_default_signal_configuration(self, signal_name, personality_id):
        response = self._invoke(
            self._client.CreateDefaultSignalConfiguration,
            grpc_types.CreateDefaultSignalConfigurationRequest(self._vi, signal_name, personality_id)
        )
        return response.status

    def get_s_parameter_external_attenuation_type(self, selector_string):
        response = self._invoke(
            self._client.GetSParameterExternalAttenuationType,
            grpc_types.GetSParameterExternalAttenuationTypeRequest(self._vi, selector_string)
        )
        return response.s_parameter_type, response.status

    def get_external_attenuation_table_actual_value(self, selector_string):
        response = self._invoke(
            self._client.GetExternalAttenuationTableActualValue,
            grpc_types.GetExternalAttenuationTableActualValueRequest(self._vi, selector_string)
        )
        return response.external_attenuation, response.status

    def get_ni_vnasdi_session(self, selector_string):
        response = self._invoke(
            self._client.GetNIVNAsdiSession,
            grpc_types.GetNIVNAsdiSessionRequest(self._vi, selector_string)
        )
        return response.ni_vnasdi_session, response.status

    def get_self_calibrate_last_temperature(self, selector_string, self_calibrate_step):
        response = self._invoke(
            self._client.GetSelfCalibrateLastTemperature,
            grpc_types.GetSelfCalibrateLastTemperatureRequest(self._vi, selector_string, self_calibrate_step)
        )
        return response.temperature, response.status

    def get_available_ports(self, selector_string):
        response = self._invoke(
            self._client.GetAvailablePorts,
            grpc_types.GetAvailablePortsRequest(self._vi, selector_string)
        )
        return response.available_ports[:], response.status

    def get_available_paths(self, selector_string):
        response = self._invoke(
            self._client.GetAvailablePaths,
            grpc_types.GetAvailablePathsRequest(self._vi, selector_string)
        )
        return response.available_paths[:], response.status
