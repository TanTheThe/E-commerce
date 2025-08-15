import React, { useCallback, useContext, useEffect, useMemo, useState } from "react";
import { Button, DialogActions, DialogContent, DialogContentText, DialogTitle, TablePagination } from "@mui/material";
import { AiOutlineEdit } from "react-icons/ai";
import { GoTrash } from "react-icons/go";
import Dialog from '@mui/material/Dialog';
import { MyContext } from "../../App";
import { deleteDataApi, getDataApi, postDataApi } from "../../utils/api";
import AddCategory from "./addCategory";
import EditCategory from "./editCategory";
import { MdChevronRight, MdExpandMore } from "react-icons/md";
import { debounce } from "lodash";
import SearchBox from "../../Components/SearchBox";

const CategoryTreeItem = ({
    category,
    children,
    level = 0,
    onEdit,
    onDelete,
    deleting,
    expandedItems,
    onToggleExpand
}) => {
    const hasChildren = children && children.length > 0;
    const isExpanded = expandedItems.includes(category.id);

    return (
        <div className="category-tree-item">
            <div
                className={`flex items-center py-3 px-4 border-b border-gray-100 hover:bg-gray-50 transition-colors
                    ${level > 0 ? 'ml-' + (level * 8) : ''}`}
                style={{ marginLeft: level * 32 }}
            >
                <div className="w-6 flex justify-center">
                    {hasChildren ? (
                        <button
                            onClick={() => onToggleExpand(category.id)}
                            className="p-1 hover:bg-gray-200 rounded transition-colors"
                        >
                            {isExpanded ? (
                                <MdExpandMore className="text-gray-600" />
                            ) : (
                                <MdChevronRight className="text-gray-600" />
                            )}
                        </button>
                    ) : (
                        <div className="w-6"></div>
                    )}
                </div>

                <div className="w-16 h-12 mx-3 flex-shrink-0">
                    <div className="w-full h-full rounded-md overflow-hidden group">
                        {category.image ? (
                            <img
                                className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                                src={category.image.startsWith('data:') ? category.image : category.image}
                                alt={category.name}
                                onError={(e) => {
                                    e.target.src = 'https://via.placeholder.com/64x48?text=No+Image';
                                }}
                            />
                        ) : (
                            <div className="w-full h-full bg-gray-200 flex items-center justify-center text-gray-400 text-xs">
                                No Image
                            </div>
                        )}
                    </div>
                </div>

                <div className="flex-grow">
                    <span className={`font-medium ${level === 0 ? 'text-gray-900 text-lg' : 'text-gray-700'}`}>
                        {category.name}
                    </span>
                    {level === 0 && hasChildren && (
                        <span className="ml-2 text-sm text-gray-500">
                            ({children.length} danh mục con)
                        </span>
                    )}
                </div>

                {level > 0 && (
                    <div className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full mr-3">
                        Level {level}
                    </div>
                )}

                <div className="flex items-center gap-2">
                    <Button
                        className="!w-8 !h-8 bg-gray-100 !border-gray-300 !rounded-full hover:!bg-gray-200 !min-w-8"
                        onClick={() => onEdit(category)}
                        title="Chỉnh sửa"
                        size="small"
                    >
                        <AiOutlineEdit className="text-gray-600 text-lg" />
                    </Button>

                    <Button
                        className="!w-8 !h-8 bg-gray-100 !border-gray-300 !rounded-full hover:!bg-red-100 !min-w-8"
                        onClick={() => onDelete(category)}
                        title="Xóa"
                        disabled={deleting}
                        size="small"
                    >
                        <GoTrash className="text-gray-600 text-lg hover:text-red-600" />
                    </Button>
                </div>
            </div>

            {hasChildren && isExpanded && (
                <div className="children">
                    {children.map(child => (
                        <CategoryTreeItem
                            key={child.category.id}
                            category={child.category}
                            children={child.children}
                            level={level + 1}
                            onEdit={onEdit}
                            onDelete={onDelete}
                            deleting={deleting}
                            expandedItems={expandedItems}
                            onToggleExpand={onToggleExpand}
                        />
                    ))}
                </div>
            )}
        </div>
    );
};

const CategoryList = () => {
    const [searchVal, setSearchVal] = useState('');
    const [categories, setCategories] = useState([]);
    const [totalCategories, setTotalCategories] = useState(0);
    const [loading, setLoading] = useState(true);
    const [rowsPerPage, setRowsPerPage] = useState(5);
    const [page, setPage] = useState(0);

    const [isOpen, setIsOpen] = useState(false);
    const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
    const [categoryToDelete, setCategoryToDelete] = useState(null);
    const [deleting, setDeleting] = useState(false);
    const [editDialogOpen, setEditDialogOpen] = useState(false);
    const [categoryToEdit, setCategoryToEdit] = useState(null);
    const [expandedItems, setExpandedItems] = useState([]);
    const [expandAll, setExpandAll] = useState(false);

    const context = useContext(MyContext);

    const buildFilterData = () => {
        const filterData = {};

        if (searchVal && searchVal.trim()) {
            filterData.search = searchVal.trim();
        }

        return filterData;
    };

    const fetchCategories = async () => {
        setLoading(true);
        try {
            const skip = page * rowsPerPage;
            const limit = rowsPerPage;

            const filterData = buildFilterData();

            const queryParams = new URLSearchParams({
                skip: skip.toString(),
                limit: limit.toString(),
            });

            if (filterData.search) queryParams.append('search', filterData.search);

            const response = await getDataApi(`/admin/categories/all?${queryParams.toString()}`);

            if (response.success) {
                setCategories(response.data.data || []);
                setTotalCategories(response.data.total || 0);
            } else {
                setCategories([]);
                setTotalCategories(0);
            }
        } catch (error) {
            console.error('Error fetching categories:', error);
            context.openAlertBox("error", "Có lỗi trong quá trình hiển thị danh mục");
            setCategories([]);
            setTotalCategories(0);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchCategories();
    }, [page, rowsPerPage, searchVal]);

    const categoryTree = useMemo(() => {
        const buildTree = (parentId = null) => {
            return categories
                .filter(cat => cat.parent_id === parentId)
                .map(category => ({
                    category,
                    children: buildTree(category.id)
                }))
                .sort((a, b) => a.category.name.localeCompare(b.category.name));
        };

        return buildTree();
    }, [categories]);

    const debouncedSearch = useCallback(
        debounce((searchTerm) => {
            console.log('Category search value changed:', searchTerm);
            setSearchVal(searchTerm);
            setPage(0);
        }, 500),
        []
    );

    const handleChangePage = (event, newPage) => {
        setPage(newPage);
    };

    const handleChangeRowsPerPage = (event) => {
        setRowsPerPage(+event.target.value);
        setPage(0);
    };

    const handleToggleExpand = (categoryId) => {
        setExpandedItems(prev =>
            prev.includes(categoryId)
                ? prev.filter(id => id !== categoryId)
                : [...prev, categoryId]
        );
    };

    const handleExpandAll = () => {
        if (expandAll) {
            setExpandedItems([]);
        } else {
            const allIds = [];
            const collectIds = (nodes) => {
                nodes.forEach(node => {
                    if (node.children.length > 0) {
                        allIds.push(node.category.id);
                        collectIds(node.children);
                    }
                });
            };
            collectIds(categoryTree);
            setExpandedItems(allIds);
        }
        setExpandAll(!expandAll);
    };

    const openDeleteDialog = (category) => {
        setCategoryToDelete(category);
        setDeleteDialogOpen(true);
    };

    const closeDeleteDialog = () => {
        setDeleteDialogOpen(false);
        setCategoryToDelete(null);
    };

    const handleDeleteCategory = async () => {
        if (!categoryToDelete) return;

        try {
            setDeleting(true);

            const response = await deleteDataApi(`/admin/categories/${categoryToDelete.id}`);

            if (response.success) {
                context.openAlertBox("success", response.message || "Xóa danh mục thành công");

                setCategories(prev =>
                    prev.filter(cat =>
                        cat.id !== categoryToDelete.id && cat.parent_id !== categoryToDelete.id
                    )
                );
                fetchCategories();
                closeDeleteDialog();
            } else {
                context.openAlertBox("error", response.message || "Có lỗi trong quá trình xóa danh mục");
            }
        } catch (error) {
            console.error('Error deleting category:', error);
            context.openAlertBox("error", "Có lỗi xảy ra khi xóa danh mục!");
        } finally {
            setDeleting(false);
        }
    };

    const handleEditCategory = (category) => {
        setCategoryToEdit(category);
        setEditDialogOpen(true);
    };

    return (
        <>
            <div className="flex items-center justify-between px-2 py-0 mt-3">
                <h2 className="text-[18px] font-[600]">
                    Danh sách các danh mục
                </h2>

                <div className="col w-[30%] ml-auto flex items-center justify-end gap-3">
                    <Button
                        className="btn-blue !text-white btn-sm"
                        onClick={() => setIsOpen(true)}
                    >
                        Tạo danh mục
                    </Button>
                    <AddCategory
                        open={isOpen}
                        onClose={() => setIsOpen(false)}
                        onSuccess={() => {
                            fetchCategories();
                        }}
                    />
                </div>
            </div>

            <div className="card my-4 pt-5 shadow-md sm:rounded-lg bg-white">
                <div className="flex items-center w-full px-5 justify-between pb-5">
                    <div className="flex items-center gap-4 w-[60%]">
                        <Button
                            onClick={handleExpandAll}
                            className="!px-4 !py-2 !text-sm !border !border-gray-300 !text-gray-700 hover:!bg-gray-50"
                            variant="outlined"
                        >
                            {expandAll ? 'Thu gọn tất cả' : 'Mở rộng tất cả'}
                        </Button>

                        <div className="text-sm text-gray-500">
                            Tổng: {totalCategories} danh mục
                        </div>
                    </div>

                    <div className="col w-[20%] ml-auto">
                        <SearchBox onSearch={debouncedSearch} />
                    </div>
                </div>

                {loading ? (
                    <div className="flex justify-center items-center py-8">
                        <div className="text-gray-500">Đang tải dữ liệu...</div>
                    </div>
                ) : (
                    <div className="category-tree">
                        {categoryTree.length === 0 ? (
                            <div className="py-8 text-center text-gray-500">
                                {totalCategories === 0 ? 'Chưa có danh mục nào' : 'Không tìm thấy danh mục phù hợp'}
                            </div>
                        ) : (
                            categoryTree.map(node => (
                                <CategoryTreeItem
                                    key={node.category.id}
                                    category={node.category}
                                    children={node.children}
                                    level={0}
                                    onEdit={handleEditCategory}
                                    onDelete={openDeleteDialog}
                                    deleting={deleting}
                                    expandedItems={expandedItems}
                                    onToggleExpand={handleToggleExpand}
                                />
                            ))
                        )}
                    </div>
                )}

                {!loading && totalCategories > 0 && (
                    <TablePagination
                        rowsPerPageOptions={[5, 10, 25, 100]}
                        component="div"
                        count={totalCategories}
                        rowsPerPage={rowsPerPage}
                        page={page}
                        onPageChange={handleChangePage}
                        onRowsPerPageChange={handleChangeRowsPerPage}
                        labelRowsPerPage="Số dòng mỗi trang:"
                        labelDisplayedRows={({ from, to, count }) => `${from}–${to} của ${count !== -1 ? count : `hơn ${to}`}`}
                    />
                )}
            </div>

            <Dialog
                open={deleteDialogOpen}
                onClose={closeDeleteDialog}
                aria-labelledby="alert-dialog-title"
                aria-describedby="alert-dialog-description"
            >
                <DialogTitle id="alert-dialog-title">
                    Xác nhận xóa danh mục
                </DialogTitle>
                <DialogContent>
                    <DialogContentText id="alert-dialog-description">
                        Bạn có chắc chắn muốn xóa danh mục "{categoryToDelete?.name}"?
                        {categoryToDelete && categories.filter(c => c.parent_id === categoryToDelete.id).length > 0 && (
                            <div className="mt-2 text-orange-600">
                                <strong>Cảnh báo:</strong> Danh mục này có danh mục con. Việc xóa sẽ xóa tất cả danh mục con.
                            </div>
                        )}
                    </DialogContentText>
                </DialogContent>
                <DialogActions>
                    <Button onClick={closeDeleteDialog} disabled={deleting}>
                        Hủy
                    </Button>
                    <Button
                        onClick={handleDeleteCategory}
                        autoFocus
                        color="error"
                        disabled={deleting}
                    >
                        {deleting ? 'Đang xóa...' : 'Xóa'}
                    </Button>
                </DialogActions>
            </Dialog>

            <EditCategory
                open={editDialogOpen}
                onClose={() => {
                    setEditDialogOpen(false);
                    setCategoryToEdit(null);
                }}
                category={categoryToEdit}
                onSuccess={() => {
                    fetchCategories();
                }}
            />
        </>
    )
}

export default CategoryList