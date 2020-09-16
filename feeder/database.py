from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import SingletonThreadPool
from .config import settings
import logging

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)

connect_args={'check_same_thread': False}   
engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True, poolclass=SingletonThreadPool, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
