from pvi.asynparam import Float64AsynParam
from pvi.record import AIRecord, AORecord


def float64(name, desc, prec, egu, autosave_fields, widget, group,
            initial_value=None, demand="AutoUpdate", readback="AutoUpdate"):

    desc_split = desc.strip("\n").split("\n")
    one_line_desc = desc_split[0]
    truncated_desc = one_line_desc[:40]

    intermediate_objects = list()
    intermediate_objects.append(Float64AsynParam(name, initial_value))

    prefix = "$(P)$(R)"
    in_out_string = "@asyn($(PORT),$(ADDR),$(TIMEOUT))" + name
    val_with_prec = "{val:.{prec}f}".format(val=initial_value, prec=prec)

    aorecord_fields = {
        "PINI": "YES",
        "DTYP": "asynFloat64",
        "OUT": in_out_string,
        "DESC": truncated_desc,
        "EGU": egu,
        "PREC": str(prec),
        "VAL": val_with_prec
    }

    aorecord_infos = {
        "autodaveFields": autosave_fields
    }

    airecord_fields = {
        "DTYP": "asynFloat64",
        "INP": in_out_string,
        "DESC": truncated_desc,
        "EGU": egu,
        "PREC": str(prec),
        "SCAN": "I/O Intr"
    }

    airecord_infos = {}

    aorecord = AORecord(prefix, name, aorecord_fields, aorecord_infos)
    intermediate_objects.append(aorecord)

    airecord = AIRecord(prefix, name + "_RBV", airecord_fields, airecord_infos)
    intermediate_objects.append(airecord)

    return intermediate_objects
