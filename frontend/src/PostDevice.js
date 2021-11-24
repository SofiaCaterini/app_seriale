import React, { useState, useEffect } from 'react';
import { useForm } from "./useForm";

import Typography from "@material-ui/core/Typography";
import TextField from "@material-ui/core/TextField";
import Button from "@material-ui/core/Button";

function PostDevice(props) {

    const [values, handleChange] = useForm({ formId: "",formNetId: "", formName: "",formLocation: "",
        formTag: "",formSensorType: "",formChar: "" });

    const postDevice = (params) => {
        fetch("http://localhost:8000/devices/", {
            method: "POST",
            headers: {
                Accept: "application/json",
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                id: params.formId,
                network_id: params.formNetId,
                name: params.formName,
                location:params.formLocation,
                time_last_measurement: params.formTag,
                sensor_type: params.formSensorType,
                characteristics: params.formChar,
            }),
        });
    };

    return (
        <div>
            <form>
                <TextField
                    label="id"
                    type="text"
                    name="formId"
                    value={values.formId}
                    onChange={handleChange}
                />
                <br />

                <TextField
                    label="network_id"
                    type="text"
                    name="formNetId"
                    value={values.formNetId}
                    onChange={handleChange}
                />
                <br />

                <TextField
                    label="name"
                    type="text"
                    name="formName"
                    value={values.formName}
                    onChange={handleChange}
                />
                <br />

                <TextField
                    label="location"
                    type="text"
                    name="formLocation"
                    value={values.formLocation}
                    onChange={handleChange}
                />
                <br />

                <TextField
                    label="time_last_measurement"
                    type="text"
                    name="formTag"
                    value={values.formTag}
                    onChange={handleChange}
                />
                <br />

                <TextField
                    label="sensor_type"
                    type="text"
                    name="formSensorType"
                    value={values.formSensorType}
                    onChange={handleChange}
                />
                <br />

                <TextField
                    label="characteristics"
                    type="text"
                    name="formChar"
                    value={values.formChar}
                    onChange={handleChange}
                />
                <br />
                <br />
                <Button
                    variant="contained"
                    type="submit"
                    value="POST -> createDevice"
                    onClick={() => postDevice(values)}
                >
                    Add device
                </Button>
            </form>
            <br />
            <br />
        </div>
    );
}

export default PostDevice;