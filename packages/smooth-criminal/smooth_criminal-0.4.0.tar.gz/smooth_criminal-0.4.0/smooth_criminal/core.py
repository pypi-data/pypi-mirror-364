import statistics
from concurrent.futures import as_completed
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool, cpu_count
import inspect
import ast

from numba import jit
import numpy as np
import asyncio
import logging
import time
from functools import wraps

from smooth_criminal.memory import log_execution_stats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SmoothCriminal")

def smooth(func):
    try:
        jit_func = jit(nopython=True, cache=True)(func)

        def wrapper(*args, **kwargs):
            logger.info("You've been hit by... a Smooth Criminal!")
            try:
                return jit_func(*args, **kwargs)
            except Exception:
                logger.warning("Beat it! Numba failed at runtime. Falling back.")
                return func(*args, **kwargs)

        return wrapper
    except Exception:
        def fallback(*args, **kwargs):
            logger.warning("Beat it! Numba failed. Falling back.")
            return func(*args, **kwargs)

        return fallback

def moonwalk(func):
    """Permite ejecutar funciones sincrónicas o asíncronas de forma asíncrona."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        logger.info("Moonwalk complete — your async function is now gliding!")

        if inspect.iscoroutinefunction(func):
            return await func(*args, **kwargs)

        if hasattr(asyncio, "to_thread"):
            return await asyncio.to_thread(func, *args, **kwargs)

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, func, *args, **kwargs)

    return wrapper

def thriller(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info("🎬 It’s close to midnight… benchmarking begins (Thriller Mode).")
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        logger.info(f"🧟 ‘Thriller’ just revealed a performance monster: {end - start:.6f} seconds.")
        return result
    return wrapper

def jam(workers=4):
    """
    Decorador que permite ejecutar funciones sobre listas en paralelo.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(args_list):
            logger.info(f"🎶 Don't stop 'til you get enough... workers! (x{workers})")
            results = []
            with ThreadPoolExecutor(max_workers=workers) as executor:
                future_to_arg = {executor.submit(func, arg): arg for arg in args_list}
                for future in as_completed(future_to_arg):
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        logger.warning(f"Worker failed on input {future_to_arg[future]}: {e}")
            return results
        return wrapper
    return decorator

def black_or_white(mode="auto"):
    """
    Optimiza tipos numéricos de arrays de entrada: float32/int32 o float64/int64.
    Modes:
        - "light": usa float32 / int32
        - "precise": usa float64 / int64
        - "auto": decide según el tamaño del array
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            converted_args = []
            for arg in args:
                if isinstance(arg, np.ndarray):
                    if mode == "light":
                        arg = _convert_to_light(arg)
                        logger.info("🌓 It's black or white! Using light types (float32/int32).")
                    elif mode == "precise":
                        arg = _convert_to_precise(arg)
                        logger.info("🌕 Going for precision! Using float64/int64.")
                    elif mode == "auto":
                        if arg.size > 1e6:
                            arg = _convert_to_light(arg)
                            logger.info("🌓 Auto mode: array is large, switching to float32/int32.")
                        else:
                            arg = _convert_to_precise(arg)
                            logger.info("🌕 Auto mode: small array, using float64/int64.")
                converted_args.append(arg)
            return func(*converted_args, **kwargs)
        return wrapper
    return decorator

def _convert_to_light(arr):
    if np.issubdtype(arr.dtype, np.integer):
        return arr.astype(np.int32)
    elif np.issubdtype(arr.dtype, np.floating):
        return arr.astype(np.float32)
    return arr

def _convert_to_precise(arr):
    if np.issubdtype(arr.dtype, np.integer):
        return arr.astype(np.int64)
    elif np.issubdtype(arr.dtype, np.floating):
        return arr.astype(np.float64)
    return arr

def beat_it(fallback_func=None):
    """
    Intenta ejecutar la función principal. Si falla, recurre al fallback.
    Si no se proporciona fallback, muestra un mensaje y lanza la excepción original.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning("🧥 Beat it! Something failed... Switching to fallback.")
                if fallback_func:
                    return fallback_func(*args, **kwargs)
                else:
                    logger.error("No fallback provided. Rethrowing exception.")
                    raise e
        return wrapper
    return decorator

def bad(parallel=False):
    """
    Aplica optimizaciones agresivas con Numba (fastmath, parallel, cache).
    Usar con precaución: puede alterar precisión numérica o portabilidad.
    """
    def decorator(func):
        try:
            jit_func = jit(nopython=True, fastmath=True, cache=True, parallel=parallel)(func)

            @wraps(func)
            def wrapper(*args, **kwargs):
                logger.info("🕶 Who's bad? This function is. Activating aggressive optimizations.")
                return jit_func(*args, **kwargs)
            return wrapper
        except Exception as e:
            logger.warning("Bad mode failed. Reverting to original function. Reason: %s", e)
            return func
    return decorator


def dangerous(func, *, parallel=True):
    """
    Modo experimental total: aplica decoradores agresivos y ejecuta benchmark.
    """
    logger.info("⚠️ Entering Dangerous Mode... Optimizing without mercy.")

    # Aplicar decoradores agresivos
    func = bad(parallel=parallel)(func)
    func = thriller(func)

    return func

def _run_once(args):
    func, func_args, func_kwargs = args
    start = time.perf_counter()
    func(*func_args, **func_kwargs)
    end = time.perf_counter()
    return end - start

def profile_it(func, args=(), kwargs=None, repeat=5, parallel=False):
    if kwargs is None:
        kwargs = {}
    """
    Ejecuta la función varias veces para obtener estadísticas de rendimiento.
    Si parallel=True, ejecuta en múltiples procesos.
    """
    logger.info("🧪 Profiling in progress... Don't stop 'til you get enough data!")

    exec_args = (func, args, kwargs)
    times = []

    if parallel:
        with Pool(min(repeat, cpu_count())) as pool:
            results = pool.map(_run_once, [exec_args] * repeat)
            times.extend(results)
    else:
        for _ in range(repeat):
            duration = _run_once(exec_args)
            times.append(duration)

    mean_time = statistics.mean(times)
    std_dev = statistics.stdev(times) if repeat > 1 else 0.0
    best_time = min(times)

    logger.info(f"⏱ Mean: {mean_time:.6f}s | Best: {best_time:.6f}s | Std dev: {std_dev:.6f}s")
    return {
        "mean": mean_time,
        "best": best_time,
        "std_dev": std_dev,
        "runs": times,
    }

def auto_boost(workers=4, fallback=None):
    """
    Decorador inteligente que detecta patrones y aplica decoradores óptimos:
    - Bucle + range() → @smooth
    - Entrada tipo list o array → @jam
    - Fallback si falla → @beat_it
    Además registra los resultados para aprendizaje posterior.
    """
    def decorator(func):
        use_jam = False
        use_smooth = False

        try:
            source = inspect.getsource(func)
            tree = ast.parse(source)

            for node in ast.walk(tree):
                if isinstance(node, ast.For):
                    if isinstance(node.iter, ast.Call) and getattr(node.iter.func, 'id', '') == 'range':
                        use_smooth = True
                elif isinstance(node, ast.Call) and getattr(node.func, 'id', '') in ['sum', 'map', 'filter']:
                    use_smooth = True

        except Exception as e:
            logger.warning(f"auto_boost: AST inspection failed: {e}")

        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal use_jam
            input_type = type(args[0]) if args else None

            if len(args) == 1 and isinstance(args[0], (list, tuple)):
                use_jam = True

            boosted = func
            decorator_used = "none"

            if fallback:
                boosted = beat_it(fallback)(boosted)
                decorator_used = "@beat_it"

            if use_smooth:
                boosted = smooth(boosted)
                decorator_used = "@smooth"
                logger.info("🧠 auto_boost: Applied @smooth")
            elif use_jam:
                boosted = jam(workers=workers)(boosted)
                decorator_used = "@jam"
                logger.info("🎶 auto_boost: Applied @jam")

            boosted = thriller(boosted)

            # Medición de tiempo para logging de memoria
            start = time.perf_counter()
            result = boosted(*args, **kwargs)
            end = time.perf_counter()

            log_execution_stats(
                func_name=func.__name__,
                input_type=input_type,
                decorator_used=decorator_used,
                duration=round(end - start, 6)
            )

            return result

        return wrapper
    return decorator
