import React, { useState } from 'react';
import { Steps } from 'antd';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import Modal from '@mui/material/Modal';


// This is a demo React components 

// Which shows react components are fully supported in vue frameworks

const style = {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    width: 400,
    bgcolor: 'background.paper',
    border: '2px solid #000',
    boxShadow: 24,
    p: 4,
};

const App = () => {
    const [count, setCount] = useState(0);
    const [open, setOpen] = useState(false);
    const description = 'This is a description.';
    const handleOpen = () => setOpen(true);
    const handleClose = () => setOpen(false);

    return (
        <div>
            <h1>App component</h1>
            <Steps
                current={1}
                items={[
                    {
                        title: 'Finished',
                        description,
                    },
                    {
                        title: 'In Progress',
                        description,
                        subTitle: 'Left 00:00:08',
                    },
                    {
                        title: 'Waiting',
                        description,
                    },
                ]}
            />
            <div style={{
                margin: '20px 0',
            }}>
                <Button onClick={handleOpen}>Open modal</Button>
            </div>
            <Modal
                open={open}
                onClose={handleClose}
                aria-labelledby="modal-modal-title"
                aria-describedby="modal-modal-description"
                >
                <Box sx={style}>
                    <Typography id="modal-modal-title" variant="h6" component="h2">
                    Text in a modal
                    </Typography>
                    <Typography id="modal-modal-description" sx={{ mt: 2 }}>
                    Duis mollis, est non commodo luctus, nisi erat porttitor ligula.
                    </Typography>
                </Box>
            </Modal>
        </div>
    );
}

export default App; 