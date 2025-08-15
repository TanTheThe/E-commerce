import React, { useState, useEffect, useRef, useContext } from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    TextField,
    Box,
    IconButton,
    Typography,
    Backdrop
} from '@mui/material';
import { IoMdClose } from "react-icons/io";
import { IoCopyOutline } from "react-icons/io5";
import { postDataApi } from '../../utils/api';

const AddColorModal = ({ open, onClose, onColorAdded, context }) => {
    const [colorName, setColorName] = useState('');
    const [selectedColor, setSelectedColor] = useState('#ff0000');
    const [hue, setHue] = useState(0);
    const [saturation, setSaturation] = useState(100);
    const [brightness, setBrightness] = useState(100);
    const [loading, setLoading] = useState(false);
    const [nameError, setNameError] = useState('');

    const colorAreaRef = useRef(null);
    const hueBarRef = useRef(null);
    const [isDraggingArea, setIsDraggingArea] = useState(false);
    const [isDraggingHue, setIsDraggingHue] = useState(false);

    const hsvToHex = (h, s, v) => {
        s /= 100;
        v /= 100;

        const c = v * s;
        const x = c * (1 - Math.abs((h / 60) % 2 - 1));
        const m = v - c;

        let r, g, b;
        if (h >= 0 && h < 60) {
            r = c; g = x; b = 0;
        } else if (h >= 60 && h < 120) {
            r = x; g = c; b = 0;
        } else if (h >= 120 && h < 180) {
            r = 0; g = c; b = x;
        } else if (h >= 180 && h < 240) {
            r = 0; g = x; b = c;
        } else if (h >= 240 && h < 300) {
            r = x; g = 0; b = c;
        } else {
            r = c; g = 0; b = x;
        }

        r = Math.round((r + m) * 255);
        g = Math.round((g + m) * 255);
        b = Math.round((b + m) * 255);

        return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
    };

    const hexToHsv = (hex) => {
        const r = parseInt(hex.slice(1, 3), 16) / 255;
        const g = parseInt(hex.slice(3, 5), 16) / 255;
        const b = parseInt(hex.slice(5, 7), 16) / 255;

        const max = Math.max(r, g, b);
        const min = Math.min(r, g, b);
        const delta = max - min;

        let h = 0;
        if (delta !== 0) {
            if (max === r) h = ((g - b) / delta) % 6;
            else if (max === g) h = (b - r) / delta + 2;
            else h = (r - g) / delta + 4;
        }
        h = Math.round(h * 60);
        if (h < 0) h += 360;

        const s = max === 0 ? 0 : Math.round((delta / max) * 100);
        const v = Math.round(max * 100);

        return [h, s, v];
    };

    useEffect(() => {
        const hex = hsvToHex(hue, saturation, brightness);
        setSelectedColor(hex);
    }, [hue, saturation, brightness]);

    const handleColorAreaMouseDown = (e) => {
        setIsDraggingArea(true);
        handleColorAreaMove(e);
    };

    const handleColorAreaMove = (e) => {
        if (!colorAreaRef.current) return;

        const rect = colorAreaRef.current.getBoundingClientRect();
        const x = Math.max(0, Math.min(e.clientX - rect.left, rect.width));
        const y = Math.max(0, Math.min(e.clientY - rect.top, rect.height));

        const newSaturation = (x / rect.width) * 100;
        const newBrightness = 100 - (y / rect.height) * 100;

        setSaturation(Math.round(newSaturation));
        setBrightness(Math.round(newBrightness));
    };

    const handleHueBarMouseDown = (e) => {
        setIsDraggingHue(true);
        handleHueBarMove(e);
    };

    const handleHueBarMove = (e) => {
        if (!hueBarRef.current) return;

        const rect = hueBarRef.current.getBoundingClientRect();
        const x = Math.max(0, Math.min(e.clientX - rect.left, rect.width));
        const newHue = (x / rect.width) * 360;

        setHue(Math.round(newHue));
    };

    useEffect(() => {
        const handleMouseMove = (e) => {
            if (isDraggingArea) handleColorAreaMove(e);
            if (isDraggingHue) handleHueBarMove(e);
        };

        const handleMouseUp = () => {
            setIsDraggingArea(false);
            setIsDraggingHue(false);
        };

        if (isDraggingArea || isDraggingHue) {
            document.addEventListener('mousemove', handleMouseMove);
            document.addEventListener('mouseup', handleMouseUp);
        }

        return () => {
            document.removeEventListener('mousemove', handleMouseMove);
            document.removeEventListener('mouseup', handleMouseUp);
        };
    }, [isDraggingArea, isDraggingHue]);

    const handleHexChange = (hex) => {
        if (/^#[0-9A-Fa-f]{6}$/.test(hex)) {
            setSelectedColor(hex);
            const [h, s, v] = hexToHsv(hex);
            setHue(h);
            setSaturation(s);
            setBrightness(v);
        }
    };

    const copyHexToClipboard = () => {
        navigator.clipboard.writeText(selectedColor.toUpperCase());
        context.openAlertBox('success', 'Đã copy mã màu!');
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!colorName.trim()) {
            setNameError('Tên màu không được để trống');
            return;
        }

        setLoading(true);
        try {
            const response = await postDataApi('/admin/color', {
                name: colorName.trim(),
                code: selectedColor.toUpperCase()
            });

            if (response.success) {
                context.openAlertBox('success', response.message || 'Thêm màu mới thành công!');
                onColorAdded();
                handleClose();
            } else {
                context.openAlertBox('error', response.message || 'Có lỗi xảy ra khi thêm màu');
            }
        } catch (error) {
            console.error('Error adding color:', error);
            context.openAlertBox('error', 'Lỗi hệ thống khi thêm màu mới');
        } finally {
            setLoading(false);
        }
    };

    const handleClose = () => {
        setColorName('');
        setSelectedColor('#ff0000');
        setHue(0);
        setSaturation(100);
        setBrightness(100);
        setNameError('');
        onClose();
    };

    return (
        <Dialog
            open={open}
            onClose={handleClose}
            maxWidth="sm"
            fullWidth
            PaperProps={{
                style: {
                    borderRadius: '12px',
                    padding: '8px'
                }
            }}
            BackdropComponent={Backdrop}
            BackdropProps={{
                style: {
                    backgroundColor: 'rgba(0, 0, 0, 0.7)',
                }
            }}
        >
            <DialogTitle sx={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '20px 24px 16px',
                borderBottom: '1px solid #e5e5e5'
            }}>
                <Typography variant="h6" component="div" sx={{ fontWeight: 600 }}>
                    Thêm màu mới
                </Typography>
                <IconButton
                    onClick={handleClose}
                    sx={{
                        color: '#666',
                        '&:hover': {
                            backgroundColor: '#f5f5f5'
                        }
                    }}
                >
                    <IoMdClose size={24} />
                </IconButton>
            </DialogTitle>

            <DialogContent sx={{ padding: '24px' }}>
                <form onSubmit={handleSubmit}>
                    <Box sx={{ mb: 3 }}>
                        <TextField
                            autoFocus
                            margin="dense"
                            label="Tên màu"
                            type="text"
                            fullWidth
                            variant="outlined"
                            value={colorName}
                            onChange={(e) => {
                                setColorName(e.target.value);
                                setNameError('');
                            }}
                            error={!!nameError}
                            helperText={nameError}
                            placeholder="Ví dụ: Đỏ Cherry, Xanh Navy..."
                            sx={{ mb: 2 }}
                        />
                    </Box>

                    <Box sx={{ mb: 3, backgroundColor: '#2c2c2c', borderRadius: '8px', padding: '20px' }}>
                        <Box
                            ref={colorAreaRef}
                            sx={{
                                width: '100%',
                                height: '200px',
                                borderRadius: '6px',
                                cursor: 'crosshair',
                                marginBottom: '16px',
                                position: 'relative',
                                background: `linear-gradient(to bottom, transparent, black),
                                           linear-gradient(to right, white, hsl(${hue}, 100%, 50%))`,
                                border: '1px solid #444'
                            }}
                            onMouseDown={handleColorAreaMouseDown}
                        >
                            <Box
                                sx={{
                                    position: 'absolute',
                                    width: '20px',
                                    height: '20px',
                                    borderRadius: '50%',
                                    border: '2px solid white',
                                    boxShadow: '0 0 0 1px rgba(0,0,0,0.3)',
                                    transform: 'translate(-50%, -50%)',
                                    left: `${saturation}%`,
                                    top: `${100 - brightness}%`,
                                    pointerEvents: 'none'
                                }}
                            />
                        </Box>

                        <Box
                            ref={hueBarRef}
                            sx={{
                                width: '100%',
                                height: '20px',
                                borderRadius: '10px',
                                cursor: 'pointer',
                                position: 'relative',
                                background: `linear-gradient(to right, 
                                    #ff0000 0%, #ffff00 17%, #00ff00 33%, 
                                    #00ffff 50%, #0000ff 67%, #ff00ff 83%, #ff0000 100%)`,
                                border: '1px solid #444',
                                marginBottom: '16px'
                            }}
                            onMouseDown={handleHueBarMouseDown}
                        >
                            <Box
                                sx={{
                                    position: 'absolute',
                                    width: '20px',
                                    height: '20px',
                                    borderRadius: '50%',
                                    border: '2px solid white',
                                    boxShadow: '0 0 0 1px rgba(0,0,0,0.3)',
                                    transform: 'translate(-50%, -50%)',
                                    left: `${(hue / 360) * 100}%`,
                                    top: '50%',
                                    pointerEvents: 'none'
                                }}
                            />
                        </Box>

                        <Box sx={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between',
                            backgroundColor: '#3a3a3a',
                            padding: '12px',
                            borderRadius: '6px',
                            border: '1px solid #444'
                        }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                <Typography
                                    variant="body2"
                                    sx={{
                                        color: '#ccc',
                                        fontSize: '14px',
                                        fontWeight: 500
                                    }}
                                >
                                    HEX
                                </Typography>
                                <Typography
                                    variant="body1"
                                    sx={{
                                        color: 'white',
                                        fontFamily: 'monospace',
                                        fontSize: '16px',
                                        fontWeight: 600,
                                        letterSpacing: '1px'
                                    }}
                                >
                                    {selectedColor.toUpperCase()}
                                </Typography>
                            </Box>
                            <IconButton
                                onClick={copyHexToClipboard}
                                sx={{
                                    color: '#ccc',
                                    '&:hover': {
                                        color: 'white',
                                        backgroundColor: '#4a4a4a'
                                    }
                                }}
                                size="small"
                            >
                                <IoCopyOutline size={18} />
                            </IconButton>
                        </Box>
                    </Box>

                    <Box sx={{ mb: 3, textAlign: 'center' }}>
                        <Typography variant="subtitle2" sx={{ mb: 2, color: '#666' }}>
                            Xem trước màu đã chọn
                        </Typography>
                        <Box
                            sx={{
                                width: 80,
                                height: 80,
                                borderRadius: '50%',
                                border: '3px solid #e0e0e0',
                                margin: '0 auto',
                                boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                                backgroundColor: selectedColor,
                                transition: 'all 0.3s ease'
                            }}
                        />
                    </Box>

                    <Box sx={{ mb: 2 }}>
                        <TextField
                            label="Mã màu HEX"
                            type="text"
                            fullWidth
                            variant="outlined"
                            value={selectedColor}
                            onChange={(e) => handleHexChange(e.target.value)}
                            placeholder="#FF0000"
                            sx={{
                                '& input': {
                                    fontFamily: 'monospace',
                                    textTransform: 'uppercase'
                                }
                            }}
                        />
                    </Box>
                </form>
            </DialogContent>

            <DialogActions sx={{
                padding: '16px 24px 24px',
                borderTop: '1px solid #e5e5e5',
                gap: '12px'
            }}>
                <Button
                    onClick={handleClose}
                    variant="outlined"
                    sx={{
                        borderColor: '#ddd',
                        color: '#666',
                        '&:hover': {
                            borderColor: '#bbb',
                            backgroundColor: '#f9f9f9'
                        }
                    }}
                >
                    Hủy
                </Button>
                <Button
                    onClick={handleSubmit}
                    variant="contained"
                    disabled={loading}
                    sx={{
                        backgroundColor: '#2196F3',
                        '&:hover': {
                            backgroundColor: '#1976D2'
                        },
                        '&:disabled': {
                            backgroundColor: '#ccc'
                        }
                    }}
                >
                    {loading ? 'Đang thêm...' : 'Thêm màu'}
                </Button>
            </DialogActions>
        </Dialog>
    );
};

export default AddColorModal;