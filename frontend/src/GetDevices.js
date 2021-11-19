import React from "react";
import { useFetch } from "./useFetch";
import { useState } from "react";

import Typography from "@material-ui/core/Typography";
import Button from "@material-ui/core/Button";

import Table from "@material-ui/core/Table";
import TableBody from "@material-ui/core/TableBody";
import TableCell from "@material-ui/core/TableCell";
import TableContainer from "@material-ui/core/TableContainer";
import TableHead from "@material-ui/core/TableHead";
import TableRow from "@material-ui/core/TableRow";
import Paper from "@material-ui/core/Paper";

const GetDevices = (params) => {
    // GET
    const { data, loading } = useFetch(
        `http://localhost:8000/devices/`
    );
    // console.log(data);

    // DELETE
    async function Blink(url) {
        await fetch(url, { method: "GET" }).then(window.location.reload());
    }


    const renderTr = (array) =>
        array.map((el) => (
            <TableRow key={el.id}>
                <TableCell>{el.id}</TableCell>
                <TableCell>
                    {" "}
                    <a href={el.url} target="_blank">
                        {el.status}
                    </a>
                </TableCell>
                <TableCell>
                    {" "}
                    <a href={el.url} target="_blank">
                        {el.time_last_measurement}
                    </a>
                </TableCell>
                <TableCell>
                    {" "}
                    <a href={el.url} target="_blank">
                        {el.sensor_type}
                    </a>
                </TableCell>


               <TableCell>
                    <Button
                        variant="contained"
                        color="primary"
                        onClick={() => Blink("http://localhost:8000/devices/" + el.id)}
                    >
                        BLINK
                    </Button>
                </TableCell>
            </TableRow>
        ));


    if (data) {
        return (
            <div>
                <Typography variant="h5">My Devices</Typography>
                <TableContainer component={Paper}>
                    <Table className="BookmarksTable" aria-label="simple table">
                        <TableHead>
                            <TableRow>
                                <TableCell>ID</TableCell>
                                <TableCell>STATUS</TableCell>
                                <TableCell>LAST MEASUREMENT</TableCell>
                                <TableCell>SENSOR TYPE</TableCell>
                                <TableCell/>
                            </TableRow>
                        </TableHead>
                        <TableBody>{renderTr(data)}</TableBody>
                    </Table>
                    {/* {console.log(typeof data)} */}
                </TableContainer>
            </div>
        );
    }

    else {
        return "Loading data...";
    }
};

export default GetDevices;