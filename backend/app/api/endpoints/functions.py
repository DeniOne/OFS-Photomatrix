from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()

@router.get("/", response_model=List[schemas.Function])
async def read_functions(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Retrieve functions."""
    functions = await crud.function.get_multi(db, skip=skip, limit=limit)
    return functions

@router.post("/", response_model=schemas.Function, status_code=status.HTTP_201_CREATED)
async def create_function(
    *, 
    db: Session = Depends(deps.get_db),
    function_in: schemas.FunctionCreate,
    current_user: models.User = Depends(deps.get_current_superuser),
) -> Any:
    """Create new function."""
    # Проверка, существует ли функция с таким кодом
    existing_function = await crud.function.get_by_code(db, code=function_in.code)
    if existing_function:
        raise HTTPException(
            status_code=400,
            detail="A function with this code already exists in the system.",
        )
    # Проверка, существует ли секция с таким ID
    section = await crud.section.get(db=db, id=function_in.section_id)
    if not section:
         raise HTTPException(
            status_code=404, 
            detail=f"Section with id {function_in.section_id} not found",
        )

    function = await crud.function.create(db=db, obj_in=function_in)
    return function

@router.get("/{function_id}", response_model=schemas.Function)
async def read_function(
    *, 
    db: Session = Depends(deps.get_db),
    function_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Get function by ID."""
    function = await crud.function.get(db=db, id=function_id)
    if not function:
        raise HTTPException(status_code=404, detail="Function not found")
    return function

@router.put("/{function_id}", response_model=schemas.Function)
async def update_function(
    *, 
    db: Session = Depends(deps.get_db),
    function_id: int,
    function_in: schemas.FunctionUpdate,
    current_user: models.User = Depends(deps.get_current_superuser),
) -> Any:
    """Update a function."""
    function = await crud.function.get(db=db, id=function_id)
    if not function:
        raise HTTPException(status_code=404, detail="Function not found")

    # Проверка уникальности кода при обновлении, если он меняется
    if function_in.code and function_in.code != function.code:
        existing_function = await crud.function.get_by_code(db, code=function_in.code)
        if existing_function and existing_function.id != function_id:
            raise HTTPException(
                status_code=400,
                detail="A function with this code already exists in the system.",
            )
            
    # Проверка существования секции при обновлении, если она меняется
    if function_in.section_id and function_in.section_id != function.section_id:
        section = await crud.section.get(db=db, id=function_in.section_id)
        if not section:
             raise HTTPException(
                status_code=404, 
                detail=f"Section with id {function_in.section_id} not found",
            )

    function = await crud.function.update(db=db, db_obj=function, obj_in=function_in)
    return function

@router.delete("/{function_id}", response_model=schemas.Function)
async def delete_function(
    *, 
    db: Session = Depends(deps.get_db),
    function_id: int,
    current_user: models.User = Depends(deps.get_current_superuser),
) -> Any:
    """Delete a function."""
    function = await crud.function.get(db=db, id=function_id)
    if not function:
        raise HTTPException(status_code=404, detail="Function not found")
    function = await crud.function.remove(db=db, id=function_id)
    return function 