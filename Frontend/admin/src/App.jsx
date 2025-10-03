import './App.css'
import { createBrowserRouter, RouterProvider, useNavigate } from "react-router-dom"
import DashBoard from './Pages/DashBoard'
import Header from './Components/Header'
import Sidebar from './Components/Sidebar'
import React, { createContext, useEffect, useState } from 'react'
import Login from './Pages/Login'
import SignUp from './Pages/SignUp'
import Products from './Pages/Products'

import Dialog from '@mui/material/Dialog';
import ListItemText from '@mui/material/ListItemText';
import ListItemButton from '@mui/material/ListItemButton';
import List from '@mui/material/List';
import Divider from '@mui/material/Divider';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import { IoMdClose } from 'react-icons/io'
import Slide from '@mui/material/Slide';
import Button from '@mui/material/Button'
import AddProduct from './Pages/Products/addProduct'
import HomeSliderBanners from './Pages/HomeSliderBanners'
import AddHomeSlide from './Pages/HomeSliderBanners/addHomeSlide'
import CategoryList from './Pages/Category/CategoryList'
import AddCategory from './Pages/Category/addCategory'
import Users from './Pages/Users'
import Orders from './Pages/Orders'
import Verify from './Pages/Verify'
import toast, { Toaster } from 'react-hot-toast'
import ForgotPassword from './Pages/ForgotPassword'
import ResetPasswordEmail from './Pages/ResetPasswordEmail'
import ResetPasswordOtp from './Pages/ResetPasswordOtp'
import SendEmailGetOtp from './Pages/SendEmailGetOtp'
import ResetPassword from './Pages/ResetPassword'
import useAuth from './Pages/Verify/auth'
import Profile from './Pages/Profile'
import EditProduct from './Pages/Products/editProduct'
import SpecialOffer from './Pages/SpecialOffer'
import Colors from './Pages/Colors'
import Reviews from './Pages/Review'
import Brands from './Pages/Brands'
import Materials from './Pages/Materials'
import Tags from './Pages/Tags'
import Staffs from './Pages/Staffs'
import Warehouse from './Pages/Warehouse'

const Transition = React.forwardRef(function Transition(
  props, ref) {
  return <Slide direction="up" ref={ref} {...props} />;
});

const MyContext = createContext()

const ProtectedRoute = ({ children, allowedRoles }) => {
  const { userData, isLoading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isLoading) {
      if (userData && !allowedRoles.includes(userData.role)) {
        navigate('/');
      }
    }
  }, [userData, isLoading, allowedRoles, navigate]);

  if (isLoading || (userData && !allowedRoles.includes(userData.role))) {
    return null;
  }

  return children;
};

function App() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true)

  const { isLogin, setIsLogin, userData, setUserData, isLoading, checkLogin } = useAuth();

  const [isOpenFullScreenPanel, setIsOpenFullScreenPanel] = useState({
    open: false,
    model: ''
  })

  const router = createBrowserRouter([
    {
      path: "/",
      exact: true,
      element: (
        <>
          <section className='main overflow-x-hidden'>
            <Header />
            <div className='contentMain flex'>
              <div className={`overflow-hidden sidebarWrapper ${isSidebarOpen === true ? 'w-[15%]' : 'w-[0px] opacity-0'} transition-all`}>
                <Sidebar />
              </div>
              <div className={`contentRight py-4 px-5 ${isSidebarOpen === false ? 'w-[100%]' : 'w-[85%]'} transition-all`}>
                <DashBoard />
              </div>
            </div>
          </section>
        </>
      )
    },
    {
      path: "/login",
      exact: true,
      element: (
        <>
          <Login />
        </>
      )
    },
    {
      path: "/signup",
      exact: true,
      element: (
        <>
          <SignUp />
        </>
      )
    },
    {
      path: "/verify",
      exact: true,
      element: (
        <>
          <Verify />
        </>
      )
    },
    {
      path: "/forgot-password",
      exact: true,
      element: (
        <>
          <ForgotPassword />
        </>
      )
    },
    {
      path: "/forgot-password-email",
      exact: true,
      element: (
        <>
          <ResetPasswordEmail />
        </>
      )
    },
    {
      path: "/forgot-password-otp",
      exact: true,
      element: (
        <>
          <ResetPasswordOtp />
        </>
      )
    },
    {
      path: "/send-mail",
      exact: true,
      element: (
        <>
          <SendEmailGetOtp />
        </>
      )
    },
    {
      path: "/reset-password/:token",
      exact: true,
      element: (
        <>
          <ResetPassword />
        </>
      )
    },
    {
      path: "/products",
      exact: true,
      element: (
        <ProtectedRoute allowedRoles={['admin']}>
          <section className='main'>
            <Header />
            <div className='contentMain flex'>
              <div className={`overflow-hidden sidebarWrapper ${isSidebarOpen === true ? 'w-[15%]' : 'w-[0px] opacity-0'} transition-all`}>
                <Sidebar />
              </div>
              <div className={`contentRight py-4 px-5 ${isSidebarOpen === false ? 'w-[100%]' : 'w-[85%]'} transition-all`}>
                <Products />
              </div>
            </div>
          </section>
        </ProtectedRoute>
      )
    },
    {
      path: "/homeSlider/list",
      exact: true,
      element: (
        <ProtectedRoute allowedRoles={['admin']}>
          <section className='main'>
            <Header />
            <div className='contentMain flex'>
              <div className={`overflow-hidden sidebarWrapper ${isSidebarOpen === true ? 'w-[15%]' : 'w-[0px] opacity-0'} transition-all`}>
                <Sidebar />
              </div>
              <div className={`contentRight py-4 px-5 ${isSidebarOpen === false ? 'w-[100%]' : 'w-[85%]'} transition-all`}>
                <HomeSliderBanners />
              </div>
            </div>
          </section>
        </ProtectedRoute>
      )
    },
    {
      path: "/category/list",
      exact: true,
      element: (
        <ProtectedRoute allowedRoles={['admin']}>
          <section className='main'>
            <Header />
            <div className='contentMain flex'>
              <div className={`overflow-hidden sidebarWrapper ${isSidebarOpen === true ? 'w-[15%]' : 'w-[0px] opacity-0'} transition-all`}>
                <Sidebar />
              </div>
              <div className={`contentRight py-4 px-5 ${isSidebarOpen === false ? 'w-[100%]' : 'w-[85%]'} transition-all`}>
                <CategoryList />
              </div>
            </div>
          </section>
        </ProtectedRoute>
      )
    },
    {
      path: "/staffs",
      exact: true,
      element: (
        <ProtectedRoute allowedRoles={['admin']}>
          <section className='main'>
            <Header />
            <div className='contentMain flex'>
              <div className={`overflow-hidden sidebarWrapper ${isSidebarOpen === true ? 'w-[15%]' : 'w-[0px] opacity-0'} transition-all`}>
                <Sidebar />
              </div>
              <div className={`contentRight py-4 px-5 ${isSidebarOpen === false ? 'w-[100%]' : 'w-[85%]'} transition-all`}>
                <Staffs />
              </div>
            </div>
          </section>
        </ProtectedRoute>
      )
    },
    {
      path: "/users",
      exact: true,
      element: (
        <ProtectedRoute allowedRoles={['admin']}>
          <section className='main'>
            <Header />
            <div className='contentMain flex'>
              <div className={`overflow-hidden sidebarWrapper ${isSidebarOpen === true ? 'w-[15%]' : 'w-[0px] opacity-0'} transition-all`}>
                <Sidebar />
              </div>
              <div className={`contentRight py-4 px-5 ${isSidebarOpen === false ? 'w-[100%]' : 'w-[85%]'} transition-all`}>
                <Users />
              </div>
            </div>
          </section>
        </ProtectedRoute>
      )
    },
    {
      path: "/orders",
      exact: true,
      element: (
        <ProtectedRoute allowedRoles={['admin']}>
          <section className='main'>
            <Header />
            <div className='contentMain flex'>
              <div className={`overflow-hidden sidebarWrapper ${isSidebarOpen === true ? 'w-[15%]' : 'w-[0px] opacity-0'} transition-all`}>
                <Sidebar />
              </div>
              <div className={`contentRight py-4 px-5 ${isSidebarOpen === false ? 'w-[100%]' : 'w-[85%]'} transition-all`}>
                <Orders />
              </div>
            </div>
          </section>
        </ProtectedRoute>
      )
    },
    {
      path: "/profile",
      exact: true,
      element: (
        <ProtectedRoute allowedRoles={['admin']}>
          <section className='main'>
            <Header />
            <div className='contentMain flex'>
              <div className={`overflow-hidden sidebarWrapper ${isSidebarOpen === true ? 'w-[15%]' : 'w-[0px] opacity-0'} transition-all`}>
                <Sidebar />
              </div>
              <div className={`contentRight py-4 px-5 ${isSidebarOpen === false ? 'w-[100%]' : 'w-[85%]'} transition-all`}>
                <Profile />
              </div>
            </div>
          </section>
        </ProtectedRoute>
      )
    },
    {
      path: "/special-offer/list",
      exact: true,
      element: (
        <ProtectedRoute allowedRoles={['admin']}>
          <section className='main'>
            <Header />
            <div className='contentMain flex'>
              <div className={`overflow-hidden sidebarWrapper ${isSidebarOpen === true ? 'w-[15%]' : 'w-[0px] opacity-0'} transition-all`}>
                <Sidebar />
              </div>
              <div className={`contentRight py-4 px-5 ${isSidebarOpen === false ? 'w-[100%]' : 'w-[85%]'} transition-all`}>
                <SpecialOffer />
              </div>
            </div>
          </section>
        </ProtectedRoute>
      )
    },
    {
      path: "/reviews/list",
      exact: true,
      element: (
        <ProtectedRoute allowedRoles={['admin']}>
          <section className='main'>
            <Header />
            <div className='contentMain flex'>
              <div className={`overflow-hidden sidebarWrapper ${isSidebarOpen === true ? 'w-[15%]' : 'w-[0px] opacity-0'} transition-all`}>
                <Sidebar />
              </div>
              <div className={`contentRight py-4 px-5 ${isSidebarOpen === false ? 'w-[100%]' : 'w-[85%]'} transition-all`}>
                <Reviews />
              </div>
            </div>
          </section>
        </ProtectedRoute>
      )
    },
    {
      path: "/colors/list",
      exact: true,
      element: (
        <ProtectedRoute allowedRoles={['admin']}>
          <section className='main'>
            <Header />
            <div className='contentMain flex'>
              <div className={`overflow-hidden sidebarWrapper ${isSidebarOpen === true ? 'w-[15%]' : 'w-[0px] opacity-0'} transition-all`}>
                <Sidebar />
              </div>
              <div className={`contentRight py-4 px-5 ${isSidebarOpen === false ? 'w-[100%]' : 'w-[85%]'} transition-all`}>
                <Colors />
              </div>
            </div>
          </section>
        </ProtectedRoute>
      )
    },
    {
      path: "/brands/list",
      exact: true,
      element: (
        <ProtectedRoute allowedRoles={['admin']}>
          <section className='main'>
            <Header />
            <div className='contentMain flex'>
              <div className={`overflow-hidden sidebarWrapper ${isSidebarOpen === true ? 'w-[15%]' : 'w-[0px] opacity-0'} transition-all`}>
                <Sidebar />
              </div>
              <div className={`contentRight py-4 px-5 ${isSidebarOpen === false ? 'w-[100%]' : 'w-[85%]'} transition-all`}>
                <Brands />
              </div>
            </div>
          </section>
        </ProtectedRoute>
      )
    },
    {
      path: "/materials/list",
      exact: true,
      element: (
        <ProtectedRoute allowedRoles={['admin']}>
          <section className='main'>
            <Header />
            <div className='contentMain flex'>
              <div className={`overflow-hidden sidebarWrapper ${isSidebarOpen === true ? 'w-[15%]' : 'w-[0px] opacity-0'} transition-all`}>
                <Sidebar />
              </div>
              <div className={`contentRight py-4 px-5 ${isSidebarOpen === false ? 'w-[100%]' : 'w-[85%]'} transition-all`}>
                <Materials />
              </div>
            </div>
          </section>
        </ProtectedRoute>
      )
    },
    {
      path: "/tags/list",
      exact: true,
      element: (
        <ProtectedRoute allowedRoles={['admin']}>
          <section className='main'>
            <Header />
            <div className='contentMain flex'>
              <div className={`overflow-hidden sidebarWrapper ${isSidebarOpen === true ? 'w-[15%]' : 'w-[0px] opacity-0'} transition-all`}>
                <Sidebar />
              </div>
              <div className={`contentRight py-4 px-5 ${isSidebarOpen === false ? 'w-[100%]' : 'w-[85%]'} transition-all`}>
                <Tags />
              </div>
            </div>
          </section>
        </ProtectedRoute>
      )
    },
    {
      path: "/warehouses/list",
      exact: true,
      element: (
        <ProtectedRoute allowedRoles={['admin', "staff"]}>
          <section className='main'>
            <Header />
            <div className='contentMain flex'>
              <div className={`overflow-hidden sidebarWrapper ${isSidebarOpen === true ? 'w-[15%]' : 'w-[0px] opacity-0'} transition-all`}>
                <Sidebar />
              </div>
              <div className={`contentRight py-4 px-5 ${isSidebarOpen === false ? 'w-[100%]' : 'w-[85%]'} transition-all`}>
                <Warehouse />
              </div>
            </div>
          </section>
        </ProtectedRoute>
      )
    },
  ])

  const openAlertBox = (status, msg) => {
    if (status === "success") {
      toast.success(msg)
    }
    if (status === "error") {
      toast.error(msg)
    }
  }

  const values = {
    isSidebarOpen,
    setIsSidebarOpen,
    isLogin,
    setIsLogin,
    isOpenFullScreenPanel,
    setIsOpenFullScreenPanel,
    openAlertBox,
    userData,
    setUserData,
    isLoading,
    checkLogin
  }

  return (
    <>
      <MyContext.Provider value={values}>
        <RouterProvider router={router} />
        <Toaster position="top-center" reverseOrder={false} />
        <Dialog
          fullScreen
          open={isOpenFullScreenPanel.open}
          onClose={() => setIsOpenFullScreenPanel({
            open: false
          })}
          slots={{
            transition: Transition,
          }}
        >
          <AppBar sx={{ position: 'relative' }}>
            <Toolbar>
              <IconButton
                edge="start"
                color="inherit"
                onClick={() => setIsOpenFullScreenPanel({
                  open: false
                })}
                aria-label="close"
              >
                <IoMdClose className='text-gray-800' />
              </IconButton>
              <Typography sx={{ ml: 2, flex: 1 }} variant="h6" component="div">
                <span className='text-gray-800'>{isOpenFullScreenPanel?.model}</span>
              </Typography>
            </Toolbar>
          </AppBar>
          {
            isOpenFullScreenPanel?.model === 'Add Product' && <AddProduct />
          }
          {
            isOpenFullScreenPanel?.model === 'Add Home Slide' && <AddHomeSlide />
          }
          {
            isOpenFullScreenPanel?.model === 'Add New Category' && <AddCategory />
          }
          {isOpenFullScreenPanel?.model === 'Update Product' && (
            <EditProduct
              productId={isOpenFullScreenPanel?.productId}
              onClose={() => setIsOpenFullScreenPanel({ open: false })}
            />
          )}
        </Dialog>
      </MyContext.Provider>
    </>
  )
}

export default App
export { MyContext }
