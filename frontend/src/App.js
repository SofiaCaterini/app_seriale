import React from "react";
import ReactDOM from "react-dom";
import Container from "@material-ui/core/Container";
import Typography from "@material-ui/core/Typography";

import PostDevice from "./PostDevice.js";
import GetDevices from "./GetDevices";

function App() {
    return (
        <div className="App">
            <Container>
                <br />
                <Typography variant="h4">Device Configuration</Typography>
                <hr />
                <br />

                <br />

                <GetDevices/>
                <br />

            </Container>
        </div>
    );
}

export default App;