import React, { useState, useEffect, useContext } from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    Typography,
    Box,
    Chip,
    Card,
    CardContent,
    Grid,
    Checkbox,
    FormControlLabel,
    CircularProgress
} from '@mui/material';
import { MyContext } from '../../App';
import { getDataApi, postDataApi } from '../../utils/api';
import HierarchicalCategorySelect from '../Products/categoriesSelect';

const AssignOfferToProducts = ({ open, onClose, offer, onSuccess }) => {
    const [categories, setCategories] = useState([]);
    const [selectedCategories, setSelectedCategories] = useState([]);
    const [productsData, setProductsData] = useState({});
    const [selectedProducts, setSelectedProducts] = useState([]);
    const [loading, setLoading] = useState(false);
    const [assigning, setAssigning] = useState(false);
    const [fetchingCategories, setFetchingCategories] = useState(false);

    const context = useContext(MyContext);

    useEffect(() => {
        if (open) {
            fetchCategories();
        }
    }, [open]);

    useEffect(() => {
        if (open) {
            setSelectedCategories([]);
            setProductsData({});
            setSelectedProducts([]);
        }
    }, [open]);

    const fetchCategories = async () => {
        try {
            const queryParams = new URLSearchParams({
                skip: "0",
                limit: "1000",
            });

            const res = await getDataApi(`/admin/categories/all?${queryParams.toString()}`);
            if (res.success === true) {
                setCategories(res.data.data || []);
            } else {
                console.error("Failed to fetch categories:", res.message);
                setCategories([]);
            }
        } catch (error) {
            console.error("Error fetching categories:", error);
            setCategories([]);
        }
    };

    useEffect(() => {
        if (selectedCategories.length > 0) {
            fetchProducts();
        } else {
            setProductsData({});
            setSelectedProducts([]);
        }
    }, [selectedCategories]);

    const fetchProducts = async () => {
        try {
            setLoading(true);
            const categoriesStr = selectedCategories.join(',');
            const response = await getDataApi(`/admin/product/offer?categories_id=${categoriesStr}`);

            if (response.success) {
                setProductsData(response.data || {});
            } else {
                context.openAlertBox("error", "Có lỗi khi tải danh sách sản phẩm");
                setProductsData({});
            }
        } catch (error) {
            console.error('Error fetching products:', error);
            context.openAlertBox("error", "Lỗi hệ thống khi tải sản phẩm");
            setProductsData({});
        } finally {
            setLoading(false);
        }
    };

    const handleProductSelect = (productId, isSelected) => {
        if (isSelected) {
            setSelectedProducts(prev => [...prev, productId]);
        } else {
            setSelectedProducts(prev => prev.filter(id => id !== productId));
        }
    };

    const handleCategoryProductsSelect = (categoryProducts, selectAll) => {
        const productIds = categoryProducts.map(product => product.id);

        if (selectAll) {
            setSelectedProducts(prev => {
                const newSelected = [...prev];
                productIds.forEach(id => {
                    if (!newSelected.includes(id)) {
                        newSelected.push(id);
                    }
                });
                return newSelected;
            });
        } else {
            setSelectedProducts(prev =>
                prev.filter(id => !productIds.includes(id))
            );
        }
    };

    const handleAssignOffer = async () => {
        if (selectedProducts.length === 0) {
            context.openAlertBox("warning", "Vui lòng chọn ít nhất một sản phẩm");
            return;
        }

        try {
            setAssigning(true);

            const requestData = {
                special_offer_id: offer.id,
                product_id: selectedProducts
            };

            const response = await postDataApi('/admin/special-offer/set-offer', requestData);

            if (response.success) {
                context.openAlertBox("success", response.message || "Gắn offer thành công");
                onSuccess?.();
                onClose();
            } else {
                context.openAlertBox("error", response.message || "Có lỗi khi gắn offer");
            }
        } catch (error) {
            console.error('Error assigning offer:', error);
            context.openAlertBox("error", "Lỗi hệ thống khi gắn offer");
        } finally {
            setAssigning(false);
        }
    };

    const getTotalProductsCount = () => {
        return Object.values(productsData).reduce((total, categoryData) => {
            return total + (categoryData.products?.length || 0);
        }, 0);
    };

    const isCategoryFullySelected = (categoryProducts) => {
        return categoryProducts.every(product => selectedProducts.includes(product.id));
    };

    return (
        <Dialog
            open={open}
            onClose={onClose}
            maxWidth="lg"
            fullWidth
            PaperProps={{
                style: { minHeight: '600px' }
            }}
        >
            <DialogTitle>
                <Typography variant="h6">
                    Gắn Offer cho Sản phẩm
                </Typography>
                <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                    Offer: <strong>{offer?.name}</strong> ({offer?.code})
                </Typography>
            </DialogTitle>

            <DialogContent dividers>
                <Box sx={{ mb: 3 }}>
                    <Typography variant="subtitle1" sx={{ mb: 2 }}>
                        1. Chọn Categories:
                    </Typography>
                    {fetchingCategories ? (
                        <Box display="flex" alignItems="center" gap={2}>
                            <CircularProgress size={20} />
                            <Typography variant="body2">Đang tải categories...</Typography>
                        </Box>
                    ) : (
                        <HierarchicalCategorySelect
                            categories={categories}
                            selectedCategoryIds={selectedCategories}
                            onSelectionChange={setSelectedCategories}
                            label=""
                            placeholder="Chọn categories để lấy sản phẩm..."
                        />
                    )}
                </Box>

                {selectedCategories.length > 0 && (
                    <Box sx={{ mb: 2 }}>
                        <Typography variant="subtitle1" sx={{ mb: 2 }}>
                            2. Chọn Sản phẩm:
                        </Typography>

                        {loading ? (
                            <Box display="flex" justifyContent="center" py={4}>
                                <CircularProgress />
                                <Typography sx={{ ml: 2 }}>Đang tải sản phẩm...</Typography>
                            </Box>
                        ) : Object.keys(productsData).length === 0 ? (
                            <Typography color="textSecondary" align="center">
                                Không tìm thấy sản phẩm nào
                            </Typography>
                        ) : (
                            <Box>
                                <Box sx={{ mb: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                                    <Typography variant="body2">
                                        Tổng cộng: <strong>{getTotalProductsCount()}</strong> sản phẩm
                                        | Đã chọn: <strong>{selectedProducts.length}</strong> sản phẩm
                                    </Typography>
                                </Box>

                                {Object.entries(productsData).map(([categoryId, categoryData]) => (
                                    <Card key={categoryId} sx={{ mb: 3, border: '1px solid #e0e0e0' }}>
                                        <CardContent>
                                            <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                                <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center' }}>
                                                    {categoryData.category_info.name}
                                                    <Chip
                                                        label={`${categoryData.products.length} sản phẩm`}
                                                        size="small"
                                                        sx={{ ml: 2 }}
                                                        color="primary"
                                                        variant="outlined"
                                                    />
                                                </Typography>

                                                <FormControlLabel
                                                    control={
                                                        <Checkbox
                                                            checked={isCategoryFullySelected(categoryData.products)}
                                                            indeterminate={
                                                                categoryData.products.some(product =>
                                                                    selectedProducts.includes(product.id)
                                                                ) && !isCategoryFullySelected(categoryData.products)
                                                            }
                                                            onChange={(e) =>
                                                                handleCategoryProductsSelect(
                                                                    categoryData.products,
                                                                    e.target.checked
                                                                )
                                                            }
                                                        />
                                                    }
                                                    label="Chọn tất cả"
                                                />
                                            </Box>

                                            <Grid container spacing={2}>
                                                {categoryData.products.map((product) => (
                                                    <Grid item xs={12} sm={6} md={4} key={product.id}>
                                                        <Box
                                                            sx={{
                                                                p: 2,
                                                                border: '1px solid #e0e0e0',
                                                                borderRadius: 1,
                                                                bgcolor: selectedProducts.includes(product.id)
                                                                    ? 'primary.50' : 'background.paper',
                                                                '&:hover': { bgcolor: 'grey.50' }
                                                            }}
                                                        >
                                                            <FormControlLabel
                                                                control={
                                                                    <Checkbox
                                                                        checked={selectedProducts.includes(product.id)}
                                                                        onChange={(e) =>
                                                                            handleProductSelect(product.id, e.target.checked)
                                                                        }
                                                                    />
                                                                }
                                                                label={
                                                                    <Box>
                                                                        <Typography variant="body2" fontWeight="medium">
                                                                            {product.name}
                                                                        </Typography>
                                                                        <Typography variant="caption" color="textSecondary">
                                                                            ID: {product.id}
                                                                        </Typography>
                                                                        <Box sx={{ mt: 1 }}>
                                                                            {product.categories.map((cat) => (
                                                                                <Chip
                                                                                    key={cat.id}
                                                                                    label={cat.name}
                                                                                    size="small"
                                                                                    sx={{ mr: 0.5, mb: 0.5 }}
                                                                                    variant="outlined"
                                                                                />
                                                                            ))}
                                                                        </Box>
                                                                    </Box>
                                                                }
                                                            />
                                                        </Box>
                                                    </Grid>
                                                ))}
                                            </Grid>
                                        </CardContent>
                                    </Card>
                                ))}
                            </Box>
                        )}
                    </Box>
                )}
            </DialogContent>

            <DialogActions sx={{ p: 2 }}>
                <Button onClick={onClose} disabled={assigning}>
                    Hủy
                </Button>
                <Button
                    variant="contained"
                    onClick={handleAssignOffer}
                    disabled={assigning || selectedProducts.length === 0}
                    startIcon={assigning && <CircularProgress size={16} />}
                >
                    {assigning ? 'Đang gắn...' : `Gắn Offer (${selectedProducts.length})`}
                </Button>
            </DialogActions>
        </Dialog>
    );
};

export default AssignOfferToProducts;