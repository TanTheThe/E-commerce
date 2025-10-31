import React, { useState, useEffect } from "react";
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    TextField,
    Grid,
    Box,
    Typography,
    IconButton,
    InputAdornment,
    Backdrop,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Switch,
    FormControlLabel,
} from "@mui/material";
import { IoMdClose } from "react-icons/io";
import {
    MdPerson,
    MdPhone,
    MdEmail,
    MdLocationOn,
    MdAccountBalance,
    MdCreditCard,
    MdNote,
    MdInventory,
    MdCategory,
    MdDelete,
    MdArrowForward,
    MdSearch,
} from "react-icons/md";
import { getDataApi, postDataApi } from '../../utils/api';

const AddSupplierModal = ({ open, onClose, onSupplierAdded, context }) => {
    const [supplierName, setSupplierName] = useState('');
    const [contactPerson, setContactPerson] = useState('');
    const [phone, setPhone] = useState('');
    const [email, setEmail] = useState('');
    const [address, setAddress] = useState('');
    const [bankAccount, setBankAccount] = useState('');
    const [bankName, setBankName] = useState('');
    const [notes, setNotes] = useState('');
    const [creditLimit, setCreditLimit] = useState('');

    const [categories, setCategories] = useState([]);
    const [products, setProducts] = useState([]);
    const [selectedCategory, setSelectedCategory] = useState('');
    const [selectedProducts, setSelectedProducts] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');

    const [loading, setLoading] = useState(false);
    const [loadingData, setLoadingData] = useState(false);
    const [nameError, setNameError] = useState('');

    useEffect(() => {
        if (open) {
            fetchCategories();
        }
    }, [open]);

    useEffect(() => {
        if (selectedCategory) {
            fetchProducts(selectedCategory);
        } else {
            setProducts([]);
        }
    }, [selectedCategory]);

    const fetchCategories = async () => {
        try {
            const response = await getDataApi('/admin/categories/all/select-box');
            if (response.success) {
                setCategories(response.data);
            }
        } catch (error) {
            console.error('Error fetching categories:', error);
        }
    };

    const fetchProducts = async (categoryId) => {
        setLoadingData(true);
        try {
            const url = `/admin/product/all/select-box?category_id=${categoryId}`;
            const response = await getDataApi(url);
            if (response.success) {
                setProducts(response.data);
            }
        } catch (error) {
            console.error('Error fetching products:', error);
        } finally {
            setLoadingData(false);
        }
    };

    const handleAddProduct = (product) => {
        if (!product) return;

        const exists = selectedProducts.find(p => p.product_id === product.id);
        if (!exists) {
            setSelectedProducts([...selectedProducts, {
                product_id: product.id,
                product_name: product.name,
                is_active: true,
                notes: ''
            }]);
        }
    };

    const handleRemoveProduct = (productId) => {
        setSelectedProducts(selectedProducts.filter(p => p.product_id !== productId));
    };

    const handleUpdateProductStatus = (productId, isActive) => {
        setSelectedProducts(selectedProducts.map(p =>
            p.product_id === productId ? { ...p, is_active: isActive } : p
        ));
    };

    const handleUpdateProductNotes = (productId, notes) => {
        setSelectedProducts(selectedProducts.map(p =>
            p.product_id === productId ? { ...p, notes } : p
        ));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!supplierName.trim()) {
            setNameError('Tên nhà cung cấp không được để trống');
            return;
        }

        setLoading(true);
        try {
            const requestData = {
                name: supplierName.trim(),
                contact_person: contactPerson.trim() || null,
                phone: phone.trim() || null,
                email: email.trim() || null,
                address: address.trim() || null,
                bank_account: bankAccount.trim() || null,
                bank_name: bankName.trim() || null,
                credit_limit: creditLimit !== '' ? parseInt(creditLimit) : null,
                notes: notes.trim() || null,
                products: selectedProducts.map(p => ({
                    product_id: p.product_id,
                    is_active: p.is_active,
                    notes: p.notes || null
                }))
            };

            const response = await postDataApi('/admin/suppliers', requestData);

            if (response.success) {
                context.openAlertBox('success', response.message || 'Thêm nhà cung cấp mới thành công!');
                onSupplierAdded();
                handleClose();
            } else {
                context.openAlertBox('error', response?.data?.detail?.message || 'Có lỗi xảy ra khi thêm nhà cung cấp');
            }
        } catch (error) {
            console.error('Error adding supplier:', error);
            context.openAlertBox('error', 'Lỗi hệ thống khi thêm nhà cung cấp mới');
        } finally {
            setLoading(false);
        }
    };

    const handleClose = () => {
        setSupplierName('');
        setContactPerson('');
        setPhone('');
        setEmail('');
        setAddress('');
        setBankAccount('');
        setBankName('');
        setCreditLimit('');
        setNotes('');
        setSelectedProducts([]);
        setSelectedCategory('');
        setSearchTerm('');
        setNameError('');
        onClose();
    };

    const formatCurrency = (value) => {
        if (!value) return '';
        return new Intl.NumberFormat('vi-VN').format(value);
    };

    const filteredProducts = products.filter(p =>
        p.name.toLowerCase().includes(searchTerm.toLowerCase()) &&
        !selectedProducts.find(sp => sp.product_id === p.id)
    );

    return (
        <Dialog
            open={open}
            onClose={handleClose}
            maxWidth="lg"
            fullWidth
            PaperProps={{
                style: {
                    borderRadius: '20px',
                    maxHeight: '92vh',
                    boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
                    fontFamily: "'Montserrat', sans-serif"
                }
            }}
            BackdropComponent={Backdrop}
            BackdropProps={{
                style: {
                    backgroundColor: 'rgba(0, 0, 0, 0.75)',
                }
            }}
        >
            <DialogTitle sx={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '24px 32px',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                borderBottom: 'none',
                fontFamily: "'Montserrat', sans-serif"
            }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Box sx={{
                        width: 48,
                        height: 48,
                        borderRadius: '12px',
                        backgroundColor: 'rgba(255,255,255,0.2)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '24px'
                    }}>
                        🏢
                    </Box>
                    <Box>
                        <Typography variant="h5" sx={{ fontWeight: 700, mb: 0.5 }}>
                            Thêm Nhà Cung Cấp Mới
                        </Typography>
                        <Typography variant="body2" sx={{ opacity: 0.9, fontSize: '13px' }}>
                            Điền thông tin chi tiết về nhà cung cấp
                        </Typography>
                    </Box>
                </Box>
                <IconButton
                    onClick={handleClose}
                    sx={{
                        color: 'white',
                        backgroundColor: 'rgba(255,255,255,0.1)',
                        '&:hover': {
                            backgroundColor: 'rgba(255,255,255,0.2)',
                            transform: 'rotate(90deg)',
                            transition: 'all 0.3s ease'
                        }
                    }}
                >
                    <IoMdClose size={24} />
                </IconButton>
            </DialogTitle>

            <DialogContent sx={{ padding: '32px', overflowY: 'auto', backgroundColor: '#f8f9fc' }}>
                <form onSubmit={handleSubmit}>
                    <Grid container spacing={3}>
                        {/* Left Column - Basic Info */}
                        <Grid item xs={12} md={7}>
                            <div className="bg-white rounded-2xl p-6 mb-4 shadow-sm border border-gray-100">
                                <div className="flex items-center mb-4">
                                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-600 to-indigo-600 flex items-center justify-center text-white mr-3">
                                        <MdPerson size={22} />
                                    </div>
                                    <h3 className="text-lg font-semibold text-gray-800">Thông tin cơ bản</h3>
                                </div>

                                <Grid container spacing={2.5}>
                                    <Grid item xs={12}>
                                        <TextField
                                            autoFocus
                                            label="Tên Nhà Cung Cấp"
                                            fullWidth
                                            variant="outlined"
                                            value={supplierName}
                                            onChange={(e) => {
                                                setSupplierName(e.target.value);
                                                setNameError('');
                                            }}
                                            error={!!nameError}
                                            helperText={nameError}
                                            placeholder="Nhập tên công ty hoặc cá nhân"
                                            required
                                            sx={{
                                                '& .MuiOutlinedInput-root': {
                                                    borderRadius: '12px',
                                                    backgroundColor: '#fafbfc'
                                                }
                                            }}
                                        />
                                    </Grid>

                                    <Grid item xs={12} sm={6}>
                                        <TextField
                                            label="Người liên hệ"
                                            fullWidth
                                            variant="outlined"
                                            value={contactPerson}
                                            onChange={(e) => setContactPerson(e.target.value)}
                                            placeholder="Họ và tên"
                                            InputProps={{
                                                startAdornment: (
                                                    <InputAdornment position="start">
                                                        <MdPerson color="#667eea" size={20} />
                                                    </InputAdornment>
                                                )
                                            }}
                                            sx={{
                                                '& .MuiOutlinedInput-root': {
                                                    borderRadius: '12px',
                                                    backgroundColor: '#fafbfc'
                                                }
                                            }}
                                        />
                                    </Grid>

                                    <Grid item xs={12} sm={6}>
                                        <TextField
                                            label="Số điện thoại"
                                            type="tel"
                                            fullWidth
                                            variant="outlined"
                                            value={phone}
                                            onChange={(e) => setPhone(e.target.value)}
                                            placeholder="0901234567"
                                            InputProps={{
                                                startAdornment: (
                                                    <InputAdornment position="start">
                                                        <MdPhone color="#667eea" size={20} />
                                                    </InputAdornment>
                                                )
                                            }}
                                            sx={{
                                                '& .MuiOutlinedInput-root': {
                                                    borderRadius: '12px',
                                                    backgroundColor: '#fafbfc'
                                                }
                                            }}
                                        />
                                    </Grid>

                                    <Grid item xs={12}>
                                        <TextField
                                            label="Email"
                                            type="email"
                                            fullWidth
                                            variant="outlined"
                                            value={email}
                                            onChange={(e) => setEmail(e.target.value)}
                                            placeholder="contact@company.com"
                                            InputProps={{
                                                startAdornment: (
                                                    <InputAdornment position="start">
                                                        <MdEmail color="#667eea" size={20} />
                                                    </InputAdornment>
                                                )
                                            }}
                                            sx={{
                                                '& .MuiOutlinedInput-root': {
                                                    borderRadius: '12px',
                                                    backgroundColor: '#fafbfc'
                                                }
                                            }}
                                        />
                                    </Grid>

                                    <Grid item xs={12}>
                                        <TextField
                                            label="Địa chỉ"
                                            fullWidth
                                            variant="outlined"
                                            value={address}
                                            onChange={(e) => setAddress(e.target.value)}
                                            placeholder="Số nhà, đường, phường/xã, quận/huyện, tỉnh/thành phố"
                                            multiline
                                            rows={2}
                                            InputProps={{
                                                startAdornment: (
                                                    <InputAdornment position="start" sx={{ alignSelf: 'flex-start', mt: 2 }}>
                                                        <MdLocationOn color="#667eea" size={20} />
                                                    </InputAdornment>
                                                )
                                            }}
                                            sx={{
                                                '& .MuiOutlinedInput-root': {
                                                    borderRadius: '12px',
                                                    backgroundColor: '#fafbfc'
                                                }
                                            }}
                                        />
                                    </Grid>
                                </Grid>
                            </div>

                            <div className="bg-white rounded-2xl p-6 mb-4 shadow-sm border border-gray-100">
                                <div className="flex items-center mb-4">
                                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-pink-500 to-red-500 flex items-center justify-center text-white mr-3">
                                        <MdAccountBalance size={22} />
                                    </div>
                                    <h3 className="text-lg font-semibold text-gray-800">Thông tin thanh toán</h3>
                                </div>

                                <Grid container spacing={2.5}>
                                    <Grid item xs={12} sm={6}>
                                        <TextField
                                            label="Tên ngân hàng"
                                            fullWidth
                                            variant="outlined"
                                            value={bankName}
                                            onChange={(e) => setBankName(e.target.value)}
                                            placeholder="Vietcombank, ACB, Techcombank..."
                                            InputProps={{
                                                startAdornment: (
                                                    <InputAdornment position="start">
                                                        <MdAccountBalance color="#f5576c" size={20} />
                                                    </InputAdornment>
                                                )
                                            }}
                                            sx={{
                                                '& .MuiOutlinedInput-root': {
                                                    borderRadius: '12px',
                                                    backgroundColor: '#fafbfc'
                                                }
                                            }}
                                        />
                                    </Grid>

                                    <Grid item xs={12} sm={6}>
                                        <TextField
                                            label="Số tài khoản"
                                            fullWidth
                                            variant="outlined"
                                            value={bankAccount}
                                            onChange={(e) => setBankAccount(e.target.value)}
                                            placeholder="1234567890"
                                            InputProps={{
                                                startAdornment: (
                                                    <InputAdornment position="start">
                                                        <MdCreditCard color="#f5576c" size={20} />
                                                    </InputAdornment>
                                                )
                                            }}
                                            sx={{
                                                '& .MuiOutlinedInput-root': {
                                                    borderRadius: '12px',
                                                    backgroundColor: '#fafbfc'
                                                }
                                            }}
                                        />
                                    </Grid>

                                    <Grid item xs={12}>
                                        <TextField
                                            label="Hạn mức công nợ"
                                            type="number"
                                            fullWidth
                                            variant="outlined"
                                            value={creditLimit}
                                            onChange={(e) => setCreditLimit(e.target.value)}
                                            InputProps={{
                                                inputProps: { min: 0 },
                                                endAdornment: (
                                                    <InputAdornment position="end">
                                                        <Typography sx={{ color: '#667eea', fontWeight: 600 }}>
                                                            VNĐ
                                                        </Typography>
                                                    </InputAdornment>
                                                )
                                            }}
                                            helperText={creditLimit ? `≈ ${formatCurrency(creditLimit)} VNĐ` : 'Để trống nếu không giới hạn'}
                                            sx={{
                                                '& .MuiOutlinedInput-root': {
                                                    borderRadius: '12px',
                                                    backgroundColor: '#fafbfc'
                                                }
                                            }}
                                        />
                                    </Grid>
                                </Grid>
                            </div>

                            <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
                                <div className="flex items-center mb-4">
                                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-green-400 to-cyan-400 flex items-center justify-center text-white mr-3">
                                        <MdNote size={22} />
                                    </div>
                                    <h3 className="text-lg font-semibold text-gray-800">Ghi chú bổ sung</h3>
                                </div>

                                <TextField
                                    label="Ghi chú chung"
                                    fullWidth
                                    multiline
                                    rows={4}
                                    variant="outlined"
                                    value={notes}
                                    onChange={(e) => setNotes(e.target.value)}
                                    placeholder="Thông tin bổ sung, điều khoản đặc biệt, lưu ý quan trọng về nhà cung cấp..."
                                    sx={{
                                        '& .MuiOutlinedInput-root': {
                                            borderRadius: '12px',
                                            backgroundColor: '#fafbfc'
                                        }
                                    }}
                                />
                            </div>
                        </Grid>

                        {/* Right Column - Products */}
                        <Grid item xs={12} md={5}>
                            <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
                                <div className="flex items-center justify-between mb-4">
                                    <div className="flex items-center">
                                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-400 flex items-center justify-center text-white mr-3">
                                            <MdInventory size={22} />
                                        </div>
                                        <div>
                                            <h3 className="text-lg font-semibold text-gray-800">Sản phẩm cung cấp</h3>
                                            {selectedProducts.length > 0 && (
                                                <p className="text-xs text-purple-600 font-semibold">
                                                    {selectedProducts.length} sản phẩm đã chọn
                                                </p>
                                            )}
                                        </div>
                                    </div>
                                </div>

                                <div className="grid grid-cols-12 gap-3 mb-4">
                                    {/* Left Side - Category & Product List */}
                                    <div className="col-span-5 space-y-3">
                                        <FormControl fullWidth size="small">
                                            <InputLabel>Danh mục</InputLabel>
                                            <Select
                                                value={selectedCategory}
                                                onChange={(e) => setSelectedCategory(e.target.value)}
                                                label="Danh mục"
                                                sx={{
                                                    borderRadius: '10px',
                                                    backgroundColor: '#fafbfc'
                                                }}
                                            >
                                                <MenuItem value="">
                                                    <em>Chọn danh mục</em>
                                                </MenuItem>
                                                {categories.map((cat) => (
                                                    <MenuItem key={cat.id} value={cat.id}>
                                                        {cat.name}
                                                    </MenuItem>
                                                ))}
                                            </Select>
                                        </FormControl>

                                        <TextField
                                            size="small"
                                            fullWidth
                                            placeholder="Tìm sản phẩm..."
                                            value={searchTerm}
                                            onChange={(e) => setSearchTerm(e.target.value)}
                                            InputProps={{
                                                startAdornment: (
                                                    <InputAdornment position="start">
                                                        <MdSearch color="#94a3b8" size={20} />
                                                    </InputAdornment>
                                                )
                                            }}
                                            sx={{
                                                '& .MuiOutlinedInput-root': {
                                                    borderRadius: '10px',
                                                    backgroundColor: '#fafbfc'
                                                }
                                            }}
                                        />

                                        <div className="border border-gray-200 rounded-xl max-h-96 overflow-y-auto bg-gray-50">
                                            {loadingData ? (
                                                <div className="flex items-center justify-center py-8">
                                                    <div className="w-6 h-6 border-2 border-purple-600 border-t-transparent rounded-full animate-spin"></div>
                                                </div>
                                            ) : !selectedCategory ? (
                                                <div className="text-center py-8 text-gray-400 text-sm">
                                                    <MdCategory size={32} className="mx-auto mb-2 opacity-50" />
                                                    <p>Chọn danh mục để xem sản phẩm</p>
                                                </div>
                                            ) : filteredProducts.length === 0 ? (
                                                <div className="text-center py-8 text-gray-400 text-sm">
                                                    <MdInventory size={32} className="mx-auto mb-2 opacity-50" />
                                                    <p>Không tìm thấy sản phẩm</p>
                                                </div>
                                            ) : (
                                                filteredProducts.map((product) => (
                                                    <div
                                                        key={product.id}
                                                        className="flex items-center justify-between p-2.5 border-b border-gray-200 hover:bg-white transition-colors group"
                                                    >
                                                        <span className="text-sm text-gray-700 flex-1 mr-2 line-clamp-2">
                                                            {product.name}
                                                        </span>
                                                        <button
                                                            type="button"
                                                            onClick={() => handleAddProduct(product)}
                                                            className="w-7 h-7 rounded-lg bg-purple-100 text-purple-600 hover:bg-purple-600 hover:text-white transition-all flex items-center justify-center flex-shrink-0 group-hover:scale-110"
                                                        >
                                                            <MdArrowForward size={16} />
                                                        </button>
                                                    </div>
                                                ))
                                            )}
                                        </div>
                                    </div>

                                    {/* Right Side - Selected Products */}
                                    <div className="col-span-7">
                                        <div className="border border-purple-200 rounded-xl bg-purple-50/30 min-h-[450px] max-h-[500px] overflow-y-auto p-3">
                                            {selectedProducts.length === 0 ? (
                                                <div className="flex flex-col items-center justify-center h-full text-gray-400 text-sm">
                                                    <MdInventory size={48} className="mb-3 opacity-30" />
                                                    <p className="font-medium">Chưa có sản phẩm</p>
                                                    <p className="text-xs mt-1">Chọn từ danh sách bên trái</p>
                                                </div>
                                            ) : (
                                                <div className="space-y-2">
                                                    {selectedProducts.map((product) => (
                                                        <div
                                                            key={product.product_id}
                                                            className="bg-white border border-gray-200 rounded-lg p-3 hover:shadow-md transition-shadow"
                                                        >
                                                            <div className="flex justify-between items-start mb-2">
                                                                <div className="flex-1 mr-2">
                                                                    <p className="text-sm font-semibold text-gray-800 mb-1 line-clamp-2">
                                                                        {product.product_name}
                                                                    </p>
                                                                    <FormControlLabel
                                                                        control={
                                                                            <Switch
                                                                                checked={product.is_active}
                                                                                onChange={(e) => handleUpdateProductStatus(product.product_id, e.target.checked)}
                                                                                size="small"
                                                                                sx={{
                                                                                    '& .MuiSwitch-switchBase.Mui-checked': {
                                                                                        color: '#4caf50'
                                                                                    },
                                                                                    '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                                                                                        backgroundColor: '#4caf50'
                                                                                    }
                                                                                }}
                                                                            />
                                                                        }
                                                                        label={
                                                                            <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${product.is_active
                                                                                    ? 'bg-green-100 text-green-700'
                                                                                    : 'bg-red-100 text-red-700'
                                                                                }`}>
                                                                                {product.is_active ? 'Hoạt động' : 'Tạm ngưng'}
                                                                            </span>
                                                                        }
                                                                        sx={{ margin: 0 }}
                                                                    />
                                                                </div>
                                                                <button
                                                                    type="button"
                                                                    onClick={() => handleRemoveProduct(product.product_id)}
                                                                    className="w-8 h-8 rounded-lg bg-red-100 text-red-600 hover:bg-red-600 hover:text-white transition-colors flex items-center justify-center flex-shrink-0"
                                                                >
                                                                    <MdDelete size={16} />
                                                                </button>
                                                            </div>
                                                            <TextField
                                                                size="small"
                                                                fullWidth
                                                                placeholder="Ghi chú..."
                                                                value={product.notes}
                                                                onChange={(e) => handleUpdateProductNotes(product.product_id, e.target.value)}
                                                                variant="outlined"
                                                                sx={{
                                                                    '& .MuiOutlinedInput-root': {
                                                                        borderRadius: '8px',
                                                                        fontSize: '13px'
                                                                    }
                                                                }}
                                                            />
                                                        </div>
                                                    ))}
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </Grid>
                    </Grid>
                </form>
            </DialogContent>

            <DialogActions sx={{
                padding: '20px 32px',
                backgroundColor: 'white',
                borderTop: '1px solid #e8eaf6',
                gap: 2
            }}>
                <Button
                    onClick={handleClose}
                    variant="outlined"
                    sx={{
                        borderRadius: '12px',
                        px: 4,
                        py: 1.2,
                        borderColor: '#e2e8f0',
                        color: '#64748b',
                        fontWeight: 600,
                        textTransform: 'none',
                        fontSize: '15px',
                        fontFamily: "'Montserrat', sans-serif",
                        '&:hover': {
                            borderColor: '#cbd5e1',
                            backgroundColor: '#f8fafc'
                        }
                    }}
                >
                    Hủy bỏ
                </Button>
                <Button
                    onClick={handleSubmit}
                    variant="contained"
                    disabled={loading || !supplierName.trim()}
                    sx={{
                        borderRadius: '12px',
                        px: 4,
                        py: 1.2,
                        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        fontWeight: 600,
                        textTransform: 'none',
                        fontSize: '15px',
                        fontFamily: "'Montserrat', sans-serif",
                        boxShadow: '0 4px 12px rgba(102,126,234,0.3)',
                        '&:hover': {
                            background: 'linear-gradient(135deg, #5568d3 0%, #6a3f8f 100%)',
                            boxShadow: '0 6px 16px rgba(102,126,234,0.4)',
                            transform: 'translateY(-1px)'
                        },
                        '&:disabled': {
                            backgroundColor: '#cbd5e1',
                            color: '#94a3b8',
                            boxShadow: 'none'
                        },
                        transition: 'all 0.2s ease'
                    }}
                >
                    {loading ? (
                        <>
                            <Box
                                component="span"
                                sx={{
                                    width: 16,
                                    height: 16,
                                    border: '2px solid rgba(255,255,255,0.3)',
                                    borderTop: '2px solid white',
                                    borderRadius: '50%',
                                    display: 'inline-block',
                                    mr: 1,
                                    animation: 'spin 0.6s linear infinite',
                                    '@keyframes spin': {
                                        '0%': { transform: 'rotate(0deg)' },
                                        '100%': { transform: 'rotate(360deg)' }
                                    }
                                }}
                            />
                            Đang xử lý...
                        </>
                    ) : (
                        '✓ Thêm Nhà Cung Cấp'
                    )}
                </Button>
            </DialogActions>
        </Dialog>
    );
};

export default AddSupplierModal;