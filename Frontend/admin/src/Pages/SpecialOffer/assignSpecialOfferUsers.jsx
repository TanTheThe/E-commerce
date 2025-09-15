import React, { useState, useEffect, useContext } from 'react';
import {
    Dialog, DialogTitle, DialogContent, DialogActions,
    Button, Typography, Box, CircularProgress,
    TextField, Table, TableBody, TableCell, TableContainer,
    TableHead, TableRow, Paper, Checkbox, Chip,
    TablePagination, Avatar
} from '@mui/material';
import { getDataApi, postDataApi } from '../../utils/api';
import { MyContext } from '../../App';

const AssignOfferToUsers = ({ open, onClose, offer, onSuccess }) => {
    const [users, setUsers] = useState([]);
    const [selectedUsers, setSelectedUsers] = useState([]);
    const [loading, setLoading] = useState(false);
    const [assigning, setAssigning] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(10);
    const [totalCount, setTotalCount] = useState(0);
    const [adminNote, setAdminNote] = useState('');

    const context = useContext(MyContext);

    useEffect(() => {
        if (open) {
            setSelectedUsers([]);
            setSearchTerm('');
            setAdminNote('');
            setPage(0);
            fetchUsers();
        }
    }, [open]);

    useEffect(() => {
        if (open) {
            const debounceTimer = setTimeout(() => {
                setPage(0);
                fetchUsers();
            }, 500);
            return () => clearTimeout(debounceTimer);
        }
    }, [searchTerm]);

    useEffect(() => {
        if (open) {
            fetchUsers();
        }
    }, [page, rowsPerPage]);

    const fetchUsers = async () => {
        try {
            setLoading(true);
            const queryParams = new URLSearchParams({
                skip: (page * rowsPerPage).toString(),
                limit: rowsPerPage.toString(),
            });

            if (searchTerm) {
                queryParams.append('search', searchTerm);
            }

            const response = await getDataApi(`/admin/user/available-for-offer/${offer.id}?${queryParams.toString()}`);

            if (response.success) {
                const responseData = response.data || response.content;
                setUsers(responseData.data || []);
                setTotalCount(responseData.total || 0);
            } else {
                context.openAlertBox("error", "Có lỗi khi tải danh sách người dùng");
                setUsers([]);
                setTotalCount(0);
            }
        } catch (error) {
            console.error('Error fetching users:', error);
            context.openAlertBox("error", "Lỗi hệ thống khi tải danh sách người dùng");
            setUsers([]);
            setTotalCount(0);
        } finally {
            setLoading(false);
        }
    };

    const handleUserSelect = (userId, isSelected) => {
        if (isSelected) {
            setSelectedUsers(prev => [...prev, userId]);
        } else {
            setSelectedUsers(prev => prev.filter(id => id !== userId));
        }
    };

    const handleSelectAll = (isSelected) => {
        if (isSelected) {
            setSelectedUsers(users.map(user => user.id));
        } else {
            setSelectedUsers([]);
        }
    };

    const isAllSelected = () => {
        return users.length > 0 && selectedUsers.length === users.length;
    };

    const isIndeterminate = () => {
        return selectedUsers.length > 0 && selectedUsers.length < users.length;
    };

    const handleAssignOffer = async () => {
        if (selectedUsers.length === 0) {
            context.openAlertBox("warning", "Vui lòng chọn ít nhất một người dùng");
            return;
        }

        try {
            setAssigning(true);

            const requestData = {
                special_offer_id: offer.id,
                user_ids: selectedUsers,
                ...(adminNote.trim() && { admin_note: adminNote.trim() })
            };

            const response = await postDataApi('/admin/special-offer/assign', requestData);

            if (response.success) {
                context.openAlertBox("success", response.message || "Gắn offer cho người dùng thành công");
                onSuccess?.();
                onClose();
            } else {
                context.openAlertBox("error", response.message || "Có lỗi khi gắn offer cho người dùng");
            }
        } catch (error) {
            console.error('Error assigning offer to users:', error);
            context.openAlertBox("error", "Lỗi hệ thống khi gắn offer cho người dùng");
        } finally {
            setAssigning(false);
        }
    };

    const handleChangePage = (event, newPage) => {
        setPage(newPage);
    };

    const handleChangeRowsPerPage = (event) => {
        setRowsPerPage(parseInt(event.target.value, 10));
        setPage(0);
    };

    const formatDate = (dateStr) => {
        return new Date(dateStr).toLocaleDateString('vi-VN');
    };

    return (
        <Dialog
            open={open}
            onClose={onClose}
            maxWidth="lg"
            fullWidth
            PaperProps={{
                style: { minHeight: '700px' }
            }}
        >
            <DialogTitle>
                <Typography variant="h6">
                    Gắn Offer cho Người dùng
                </Typography>
                <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                    Offer: <strong>{offer?.name}</strong> ({offer?.code})
                </Typography>
            </DialogTitle>

            <DialogContent dividers>
                <Box sx={{ mb: 3 }}>
                    <TextField
                        fullWidth
                        variant="outlined"
                        placeholder="Tìm kiếm người dùng theo tên, email..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        sx={{ mb: 2 }}
                    />

                    <Box sx={{ mb: 2 }}>
                        <TextField
                            fullWidth
                            multiline
                            rows={3}
                            variant="outlined"
                            label="Ghi chú (Tùy chọn)"
                            placeholder="Nhập ghi chú để gửi cùng với thông báo khuyến mãi..."
                            value={adminNote}
                            onChange={(e) => setAdminNote(e.target.value)}
                            helperText={`${adminNote.length}/500 ký tự. Ghi chú này sẽ được gửi kèm trong thông báo.`}
                            inputProps={{
                                maxLength: 500
                            }}
                            sx={{
                                '& .MuiOutlinedInput-root': {
                                    '&:hover fieldset': {
                                        borderColor: 'primary.main',
                                    },
                                },
                            }}
                        />
                    </Box>

                    <Box sx={{ mb: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                        <Typography variant="body2">
                            Tổng cộng: <strong>{totalCount}</strong> người dùng
                            | Đã chọn: <strong>{selectedUsers.length}</strong> người dùng
                        </Typography>
                    </Box>

                    {loading ? (
                        <Box display="flex" justifyContent="center" py={4}>
                            <CircularProgress />
                            <Typography sx={{ ml: 2 }}>Đang tải danh sách người dùng...</Typography>
                        </Box>
                    ) : (
                        <Paper sx={{ width: '100%' }}>
                            <TableContainer sx={{ maxHeight: 400 }}>
                                <Table stickyHeader>
                                    <TableHead>
                                        <TableRow>
                                            <TableCell padding="checkbox">
                                                <Checkbox
                                                    checked={isAllSelected()}
                                                    indeterminate={isIndeterminate()}
                                                    onChange={(e) => handleSelectAll(e.target.checked)}
                                                />
                                            </TableCell>
                                            <TableCell>Họ tên</TableCell>
                                            <TableCell>Email</TableCell>
                                            <TableCell>Số điện thoại</TableCell>
                                            <TableCell>Ngày tạo</TableCell>
                                            <TableCell>Trạng thái</TableCell>
                                        </TableRow>
                                    </TableHead>
                                    <TableBody>
                                        {users.length === 0 ? (
                                            <TableRow>
                                                <TableCell colSpan={7} align="center">
                                                    <Typography color="textSecondary" sx={{ py: 4 }}>
                                                        Không tìm thấy người dùng nào
                                                    </Typography>
                                                </TableCell>
                                            </TableRow>
                                        ) : (
                                            users.map((user) => (
                                                <TableRow
                                                    key={user.id}
                                                    hover
                                                    selected={selectedUsers.includes(user.id)}
                                                >
                                                    <TableCell padding="checkbox">
                                                        <Checkbox
                                                            checked={selectedUsers.includes(user.id)}
                                                            onChange={(e) => handleUserSelect(user.id, e.target.checked)}
                                                        />
                                                    </TableCell>
                                                    <TableCell>
                                                        <Typography variant="body2" fontWeight="medium">
                                                            {user.first_name + " " + user.last_name || 'Chưa cập nhật'}
                                                        </Typography>
                                                    </TableCell>
                                                    <TableCell>
                                                        <Typography variant="body2">
                                                            {user.email}
                                                        </Typography>
                                                    </TableCell>
                                                    <TableCell>
                                                        <Typography variant="body2">
                                                            {user.phone || 'Chưa cập nhật'}
                                                        </Typography>
                                                    </TableCell>
                                                    <TableCell>
                                                        <Typography variant="body2">
                                                            {formatDate(user.created_at)}
                                                        </Typography>
                                                    </TableCell>
                                                    <TableCell>
                                                        <Chip
                                                            label={user.customer_status == 'active' ? 'Hoạt động' : 'Không hoạt động'}
                                                            color={user.customer_status == 'active' ? 'success' : 'default'}
                                                            size="small"
                                                        />
                                                    </TableCell>
                                                </TableRow>
                                            ))
                                        )}
                                    </TableBody>
                                </Table>
                            </TableContainer>

                            <TablePagination
                                rowsPerPageOptions={[10, 25, 50]}
                                component="div"
                                count={totalCount}
                                rowsPerPage={rowsPerPage}
                                page={page}
                                onPageChange={handleChangePage}
                                onRowsPerPageChange={handleChangeRowsPerPage}
                                labelRowsPerPage="Số hàng mỗi trang:"
                                labelDisplayedRows={({ from, to, count }) =>
                                    `${from}-${to} trong tổng số ${count !== -1 ? count : `hơn ${to}`}`
                                }
                            />
                        </Paper>
                    )}
                </Box>
            </DialogContent>

            <DialogActions sx={{ p: 2 }}>
                <Button onClick={onClose} disabled={assigning}>
                    Hủy
                </Button>
                <Button
                    variant="contained"
                    onClick={handleAssignOffer}
                    disabled={assigning || selectedUsers.length === 0}
                    startIcon={assigning && <CircularProgress size={16} />}
                >
                    {assigning ? 'Đang gắn...' : `Gắn Offer (${selectedUsers.length})`}
                </Button>
            </DialogActions>
        </Dialog>
    );
};

export default AssignOfferToUsers;